# Importação das bibliotecas necessárias
from openai import OpenAI
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurar a chave da API da OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("A chave da API 'OPENAI_API_KEY' não foi encontrada. Verifique o arquivo .env.")

# Inicializar o cliente da OpenAI
client = OpenAI(api_key=api_key)

# Histórico da conversa
conversation_history = [
    {"role": "system", "content": "Você é um assistente útil e bem informado, sempre respondendo com detalhes e clareza."}
]

def chamar_gpt(entrada_usuario):
    """
    Função que interage com o GPT-4o-mini, enviando o histórico de conversas atualizado e recebendo a resposta.
    """
    # Adicionar a entrada do usuário ao histórico
    conversation_history.append({"role": "user", "content": entrada_usuario})
    
    try:
        # Solicitar uma conclusão do modelo
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history
        )
        
        # Extrair a resposta do modelo
        response = completion.choices[0].message.content
        
        # Adicionar a resposta ao histórico
        conversation_history.append({"role": "assistant", "content": response})
        
        return response
    except Exception as e:
        return f"Ocorreu um erro ao interagir com o modelo: {e}"


# Montar prompt da aplicação
# Primeira interação
entrada_usuario = '''
    Você é um especialisata e crítico nde cinema.
    Sugira algums gêneros de filme para que eu possa selecionar e assistir.
    A resposta tem que vir em formato de lista.
'''
res = chamar_gpt(entrada_usuario)
print(res)

# Seguanda interação
# Gêneros selecionados selecionados

entrada_usuario = '''
    Ação, Terror e Drama.
    A resposta tem que vir em formato de lista.
'''
res = chamar_gpt(entrada_usuario)
print(res)

# Terceira interação
# Filmes selecionados
entrada_usuario = '''
    "Mad Max: Estrada da Fúria, O Exorcista e Um Sonho de Liberdade.
    A resposta tem que vir em formato json válido, sem outras dados adicionais e sem a marca
'''
resOriginal = chamar_gpt(entrada_usuario)
print(resOriginal)

from guardrails.hub import ValidJson
from guardrails import Guard

guard = Guard().use(ValidJson, on_fail="exception")

# Validação da resposta com o ValidJson do Hub GuardRails.
# Validação com a resposta original.
respostaAjustada = ""
try:
    guard.validate(
        resOriginal
    )  
    print("Fomatação Json está correta.")
except Exception as e:
    print(e)
    print('''
          A resposta original vindo da LLM contém dados adicionais que invalidam o conteúdo Json.
          É preciso ajustar esse conteúdo.          
          ''')
     # Ajuste do conteudo da resposta. Retirando dados adicionais que comprometem o contúdo Json
    pos1 = resOriginal.find("{")
    pos2 = resOriginal.rfind('}')
    respostaAjustada = resOriginal[slice(pos1,pos2+1)]
    # Submetemos a resposta ao validador
    try:
        guard.validate(
            respostaAjustada
        )  
        print("Fomatação Json está correta.")
    except Exception as e:
        print(e)
