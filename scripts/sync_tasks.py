import os
import re
import sys
import requests
import json

# Resolve absolute paths relative to this script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
TASKS_FILE = os.path.join(BASE_DIR, "TASKS.md")
ENV_FILE = os.path.join(BASE_DIR, ".env")

def load_env():
    env = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, val = line.split("=", 1)
                        env[key.strip()] = val.strip()
    return env

env = load_env()
GITHUB_TOKEN = env.get("GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
PROJECT_NUMBER = env.get("PROJECT_NUMBER") or os.environ.get("PROJECT_NUMBER")
GITHUB_USER = env.get("GITHUB_USER") or os.environ.get("GITHUB_USER")

if not GITHUB_TOKEN or not PROJECT_NUMBER or not GITHUB_USER:
    print("[ERRO] Variáveis GITHUB_TOKEN, PROJECT_NUMBER ou GITHUB_USER não encontradas no .env ou no ambiente.")
    sys.exit(1)

PROJECT_NUMBER = int(PROJECT_NUMBER)

def normalize_text(text):
    if not text:
        return ""
    text = text.replace("\r\n", "\n")
    # Split by lines, strip each line
    lines = [line.strip() for line in text.split("\n")]
    # Filter out empty lines from comparison to make it robust against spacing changes
    lines = [line for line in lines if line]
    return "\n".join(lines).strip()

def parse_tasks():
    if not os.path.exists(TASKS_FILE):
        print(f"[ERRO] Arquivo {TASKS_FILE} não encontrado.")
        return []
    
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    sections = content.split("---")
    tasks = []
    
    header_re = re.compile(r"###\s+(TASK-\d+)\s*[-—]\s*(.+)")
    
    for section in sections:
        section = section.strip()
        header_match = header_re.search(section)
        if not header_match:
            continue
        
        task_id = header_match.group(1)
        title = header_match.group(2).strip()
        full_title = f"{task_id} — {title}"
        
        status_match = re.search(r"\*\*Status:\*\*\s*\[(.*?)\]", section)
        status_val = status_match.group(1).strip() if status_match else ""
        
        is_done = False
        is_in_progress = False
        
        if status_val.lower() == 'x':
            is_done = True
        elif status_val == '/':
            is_in_progress = True
            
        desc_match = re.search(r"\*\*Descrição:\*\*(.*?)(?=\*\*Critérios de aceite:\*\*|$)", section, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""
        
        criteria_match = re.search(r"\*\*Critérios de aceite:\*\*(.*)$", section, re.DOTALL)
        criteria = criteria_match.group(1).strip() if criteria_match else ""
        
        body = f"### Descrição\n{description}\n\n### Critérios de aceite\n{criteria}"
        
        tasks.append({
            "id": task_id,
            "title": full_title,
            "body": body,
            "is_done": is_done,
            "is_in_progress": is_in_progress
        })
        
    return tasks

def query_github(query, variables=None):
    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    r = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    if r.status_code != 200:
        raise Exception(f"GraphQL request failed with code {r.status_code}: {r.text}")
    res = r.json()
    if "errors" in res:
        raise Exception(f"GraphQL returned errors: {res['errors']}")
    return res["data"]

def get_project_metadata():
    query = """
    query($login: String!, $number: Int!) {
      user(login: $login) {
        projectV2(number: $number) {
          id
          title
          fields(first: 50) {
            nodes {
              ... on ProjectV2SingleSelectField {
                id
                name
                options {
                  id
                  name
                }
              }
            }
          }
        }
      }
    }
    """
    data = query_github(query, {"login": GITHUB_USER, "number": PROJECT_NUMBER})
    project = data["user"]["projectV2"]
    if not project:
        raise Exception(f"Projeto #{PROJECT_NUMBER} não encontrado para o usuário {GITHUB_USER}.")
    
    project_id = project["id"]
    status_field_id = None
    status_options = {}
    
    for field in project["fields"]["nodes"]:
        if field.get("name") == "Status":
            status_field_id = field["id"]
            for option in field["options"]:
                status_options[option["name"].lower()] = option["id"]
            break
            
    if not status_field_id:
        raise Exception("Campo 'Status' não encontrado no projeto.")
        
    return project_id, status_field_id, status_options

def get_current_items(project_id):
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          items(first: 100) {
            nodes {
              id
              content {
                ... on DraftIssue {
                  id
                  title
                  body
                }
                ... on Issue {
                  title
                }
              }
              fieldValues(first: 20) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                    field {
                      ... on ProjectV2FieldCommon {
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    data = query_github(query, {"projectId": project_id})
    items = data["node"]["items"]["nodes"]
    existing = {}
    for item in items:
        title = ""
        draft_issue_id = None
        body_content = ""
        
        content = item.get("content")
        if content:
            title = content.get("title", "")
            draft_issue_id = content.get("id")
            body_content = content.get("body", "")
        
        status_name = ""
        for val in item.get("fieldValues", {}).get("nodes", []):
            if val.get("field", {}).get("name") == "Status":
                status_name = val.get("name", "")
                break
                
        if title:
            existing[title] = {
                "id": item["id"],
                "draft_issue_id": draft_issue_id,
                "status": status_name.lower(),
                "body": body_content
            }
    return existing

def add_draft_issue(project_id, title, body):
    query = """
    mutation($projectId: ID!, $title: String!, $body: String!) {
      addProjectV2DraftIssue(input: {projectId: $projectId, title: $title, body: $body}) {
        projectItem {
          id
          content {
            ... on DraftIssue {
              id
            }
          }
        }
      }
    }
    """
    data = query_github(query, {"projectId": project_id, "title": title, "body": body})
    item = data["addProjectV2DraftIssue"]["projectItem"]
    item_id = item["id"]
    draft_issue_id = item.get("content", {}).get("id") if item.get("content") else None
    return item_id, draft_issue_id

def update_draft_issue(draft_issue_id, title, body):
    query = """
    mutation($draftIssueId: ID!, $title: String!, $body: String!) {
      updateProjectV2DraftIssue(input: {
        draftIssueId: $draftIssueId
        title: $title
        body: $body
      }) {
        draftIssue {
          id
        }
      }
    }
    """
    query_github(query, {
        "draftIssueId": draft_issue_id,
        "title": title,
        "body": body
    })

def update_item_status(project_id, item_id, field_id, option_id):
    query = """
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId
        itemId: $itemId
        fieldId: $fieldId
        value: {singleSelectOptionId: $optionId}
      }) {
        projectV2Item {
          id
        }
      }
    }
    """
    query_github(query, {
        "projectId": project_id,
        "itemId": item_id,
        "fieldId": field_id,
        "optionId": option_id
    })

def main():
    print("Sincronizando tarefas com o GitHub Projects (com atualização de corpo)...")
    tasks = parse_tasks()
    print(f"Lidas {len(tasks)} tarefas de TASKS.md.")
    
    print("Buscando metadados do projeto...")
    project_id, status_field_id, status_options = get_project_metadata()
    print("Opções de Status detectadas:", list(status_options.keys()))
    
    print("Buscando itens atuais do board...")
    existing_items = get_current_items(project_id)
    
    for t in tasks:
        title = t["title"]
        body = t["body"]
        is_done = t["is_done"]
        is_in_progress = t["is_in_progress"]
        
        # Determine target status name
        if is_done:
            target_status_name = "done"
        elif is_in_progress:
            target_status_name = "in progress"
        else:
            target_status_name = "todo"
            
        # Get target option ID
        option_id = status_options.get(target_status_name)
        if not option_id:
            option_id = status_options.get("todo") or list(status_options.values())[0]
            
        if title in existing_items:
            item_info = existing_items[title]
            item_id = item_info["id"]
            draft_issue_id = item_info["draft_issue_id"]
            current_status = item_info["status"]
            current_body = item_info["body"]
            
            # Check if the body needs update
            if draft_issue_id and normalize_text(current_body) != normalize_text(body):
                print(f"Atualizando corpo de '{title}'...")
                update_draft_issue(draft_issue_id, title, body)
            
            if current_status != target_status_name:
                print(f"Atualizando status de '{title}': {current_status} -> {target_status_name}")
                update_item_status(project_id, item_id, status_field_id, option_id)
        else:
            print(f"Criando nova task '{title}' no status {target_status_name}...")
            item_id, draft_issue_id = add_draft_issue(project_id, title, body)
            update_item_status(project_id, item_id, status_field_id, option_id)
            
    print("Sincronização concluída com sucesso!")

if __name__ == "__main__":
    main()
