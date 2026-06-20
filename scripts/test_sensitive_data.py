import os
import sys
import unittest

# Adiciona o diretório dos scripts ao path para importação
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from sensitive_data import scan, has_sensitive, mask

class TestSensitiveData(unittest.TestCase):

    def test_github_token(self):
        token = "ghp_AbCdEfGhIjKlMnOpQrStUvWxYz0123456789"
        text = f"Meu token de acesso é {token}."
        
        # Teste do Scan
        findings = scan(text)
        self.assertTrue(any(f["type"] == "github_token" for f in findings))
        self.assertEqual(findings[0]["masked_preview"], "ghp_****")
        
        # Teste do Has
        self.assertTrue(has_sensitive(text))
        
        # Teste de Máscara
        masked = mask(text)
        self.assertNotIn(token, masked)
        self.assertIn("ghp_****", masked)

    def test_discord_webhook(self):
        webhook = "https://discord.com/api/webhooks/1234567890/ABCDEFG_hijklmn"
        text = f"Enviar logs para {webhook} no canal principal."
        
        # Teste do Scan
        findings = scan(text)
        self.assertTrue(any(f["type"] == "discord_webhook" for f in findings))
        self.assertEqual(findings[0]["masked_preview"], "[DISCORD_WEBHOOK]")
        
        # Teste de Máscara
        masked = mask(text)
        self.assertNotIn(webhook, masked)
        self.assertIn("[DISCORD_WEBHOOK]", masked)

    def test_api_key(self):
        text_eq = "Definir key=minha_api_key_secreta_123 nos parâmetros."
        text_colon = "api_key: outra_key_secreta_999"
        
        # Teste do Scan
        self.assertTrue(any(f["type"] == "api_key" for f in scan(text_eq)))
        self.assertTrue(any(f["type"] == "api_key" for f in scan(text_colon)))
        
        # Teste de Máscara
        self.assertIn("key=[API_KEY]", mask(text_eq))
        self.assertIn("api_key=[API_KEY]", mask(text_colon))

    def test_email(self):
        email = "usuario.teste@provedor-seguro.com.br"
        text = f"Contato através de {email} para suporte."
        
        # Teste do Scan
        findings = scan(text)
        self.assertTrue(any(f["type"] == "email" for f in findings))
        self.assertEqual(findings[0]["masked_preview"], "us***@provedor-seguro.com.br")
        
        # Teste de Máscara
        masked = mask(text)
        self.assertNotIn(email, masked)
        self.assertIn("[EMAIL]", masked)

    def test_cpf(self):
        cpf = "123.456.789-00"
        text = f"O CPF do portador é {cpf}."
        
        # Teste do Scan
        findings = scan(text)
        self.assertTrue(any(f["type"] == "cpf" for f in findings))
        self.assertEqual(findings[0]["masked_preview"], "***.***.***-**")
        
        # Teste de Máscara
        masked = mask(text)
        self.assertNotIn(cpf, masked)
        self.assertIn("[CPF]", masked)

    def test_senha(self):
        text_pass = "Minha password=SuperSenhaSegura!"
        text_senha = "Campo senha: 12345a"
        
        # Teste do Scan
        self.assertTrue(any(f["type"] == "senha" for f in scan(text_pass)))
        self.assertTrue(any(f["type"] == "senha" for f in scan(text_senha)))
        
        # Teste de Máscara
        self.assertIn("password=[SENHA]", mask(text_pass))
        self.assertIn("senha=[SENHA]", mask(text_senha))

    def test_private_key_pem(self):
        pem_header = "-----BEGIN RSA PRIVATE KEY-----"
        text = f"Importe o certificado:\n{pem_header}\nMIIEpAIBAAKCAQEA..."
        
        # Teste do Scan
        findings = scan(text)
        self.assertTrue(any(f["type"] == "chave_privada" for f in findings))
        self.assertEqual(findings[0]["masked_preview"], "[CHAVE_PRIVADA]")
        
        # Teste de Máscara
        masked = mask(text)
        self.assertNotIn(pem_header, masked)
        self.assertIn("[CHAVE_PRIVADA]", masked)

    def test_no_sensitive_data(self):
        text = "Este é um texto completamente seguro contendo apenas palavras normais."
        self.assertEqual(scan(text), [])
        self.assertFalse(has_sensitive(text))
        self.assertEqual(mask(text), text)

if __name__ == "__main__":
    unittest.main()
