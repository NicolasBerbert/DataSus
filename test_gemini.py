#!/usr/bin/env python3

"""
Teste simples para verificar se o Gemini está funcionando
"""

def test_gemini():
    print("🔍 DEBUG: Iniciando teste do Gemini...")
    
    try:
        print("🔍 DEBUG: Importando biblioteca...")
        import google.generativeai as genai
        print("✅ DEBUG: Biblioteca importada com sucesso")
        
        # Verificar versão
        try:
            version = genai.__version__
            print(f"🔍 DEBUG: Versão: {version}")
        except:
            print("⚠️  DEBUG: Não foi possível verificar versão")
        
        # Configurar API
        print("🔍 DEBUG: Configurando API...")
        genai.configure(api_key="AIzaSyC2b5xyyXkZDu_8AcVVjIlFxUFP9QM8eZU")
        print("✅ DEBUG: API configurada")
        
        # Testar modelo gemini-1.5-flash
        print("🔍 DEBUG: Testando modelo gemini-1.5-flash...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ DEBUG: Modelo criado com sucesso")
        
        # Teste simples
        print("🔍 DEBUG: Enviando teste simples...")
        response = model.generate_content("Responda apenas: TESTE OK")
        print(f"✅ DEBUG: Resposta recebida: {response.text}")
        
        # Teste SQL
        print("🔍 DEBUG: Testando geração de SQL...")
        sql_prompt = """
        Gere uma consulta SQL para contar registros na tabela 'internacoes'.
        Responda APENAS com o SQL, sem explicações.
        """
        
        sql_response = model.generate_content(sql_prompt)
        print(f"✅ DEBUG: SQL gerado: {sql_response.text}")
        
        print("🎉 DEBUG: TODOS OS TESTES PASSARAM!")
        return True
        
    except Exception as e:
        print(f"❌ DEBUG: ERRO: {str(e)}")
        print(f"❌ DEBUG: Tipo: {type(e).__name__}")
        
        import traceback
        print("❌ DEBUG: Traceback completo:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gemini()
    if success:
        print("\n✅ RESULTADO: Gemini está funcionando corretamente!")
    else:
        print("\n❌ RESULTADO: Gemini não está funcionando.")
        print("❌ SOLUÇÕES:")
        print("❌ 1. pip install --upgrade google-generativeai")
        print("❌ 2. Verificar chave da API")
        print("❌ 3. Verificar conectividade")