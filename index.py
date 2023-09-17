import streamlit as st
from moviepy.editor import *
import whisper
import io
import openai

def load_openai_key():
    with open("./openai_api_key", "r") as openai_key_file:
        os.environ['OPENAI_API_KEY'] = openai_key_file.read().strip()

    openai.api_key_path = "./openai_api_key"

def initialize_session_state():
    if 'inputvideo' not in st.session_state:
        st.session_state['inputvideo'] = None

    if 'name' not in st.session_state:
        st.session_state['name'] = 'update.io'

    if 'prompt' not in st.session_state:
        st.session_state['prompt'] = None

    if 'respfinal' not in st.session_state:
        st.session_state['respfinal'] = None

    if 'botaoconfirma' not in st.session_state:
        st.session_state['botaoconfirma'] = None

    if 'botaoprompt' not in st.session_state:
        st.session_state['botaoprompt'] = None

    if 'condicaoprompt' not in st.session_state:
        st.session_state['condicaoprompt'] = False

    if "disabled" not in st.session_state:
        st.session_state['disabled'] = False

    st.set_page_config(page_title=st.session_state['name'])
    st.title(st.session_state['name'])

def disable():
    st.session_state['disabled'] = True

def prompt_desejado():

    if st.session_state['prompt'] == 'Resumo':
        return str('Faça um resumo sobre o conteúdo transcrito abaixo, seja breve mas o mais preciso possível, não fuja do assunto em nenhuma hipótese')
    if st.session_state['prompt'] == 'Perguntas/Respostas':
        p1 = st.text_input('Pergunta 1', placeholder="Qual a sua dúvida")
        p2 = st.text_input('Pergunta 2', placeholder="Qual a sua dúvida")
        p3 = st.text_input('Pergunta 3', placeholder="Qual a sua dúvida")
        return str(f'Responda as perguntas do usuário a seguir de forma a não fugir do assunto, responda com base somente nas transcrições abaixo das perguntas \n{p1}\n{p2}\n{p3}')
    if st.session_state['prompt'] == 'Conversão de Idioma': 
        input_idioma = st.text_input('Entrada', placeholder="Idioma Original")
        output_idioma = st.text_input('Saída', placeholder="Idiomal Traduzido")
        return str(f'Faça a tradução de {input_idioma} para {output_idioma} das transcrições abaixo')
    if st.session_state['prompt'] == 'Personalizado': 
        input_personalizado = st.text_input('Entrada Personalizada', placeholder="")
        return str(input_personalizado)

def usaprompt():
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": st.session_state['respfinal']}],
        temperature = 0
    )
    response = completion['choices'][0]['message']['content']
    print(completion)
    return response

def startconvert():
    st.session_state['inputvideo'] = st.file_uploader('Carregador de arquivos', accept_multiple_files=False, type=['mp4'], label_visibility="visible")
    st.session_state['prompt'] = st.selectbox('Prompt desejado', options=["Resumo", "Perguntas/Respostas", "Conversão de Idioma", "Personalizado"])
    prompt = prompt_desejado()
    _, colbuttom, colprompt, _ = st.columns(4)
    st.session_state['botaoconfirma'] = colbuttom.button('Gerar Prompt', on_click=disable, disabled=st.session_state['disabled'])
    st.session_state['botaoprompt'] = colprompt.button("Usar Prompt")
    if st.session_state['botaoconfirma']:
        with open("input//video_file.mp4", 'wb') as out:  
            out.write(io.BytesIO(st.session_state['inputvideo'].read()).read())  
        out.close()

        # Conversão do .mp4 p/ .mp3 
        video = VideoFileClip("input//video_file.mp4")
        video.audio.write_audiofile(f"input//audio_file.mp3")

        # Transcrição do .mp3 p/ texto com o uso do whisper
        model = whisper.load_model("base")
        result = model.transcribe("input//audio_file.mp3", fp16=False, language='Portuguese')
        
        st.session_state['respfinal'] = st.text_area('Prompt do usuário', '''{prompt}\n\n{result}'''.format(result=result["text"], prompt=prompt), label_visibility="visible", height=750)
        st.session_state['condicaoprompt'] = True
        st.session_state['disabled'] = False

    if st.session_state['botaoprompt'] and st.session_state['condicaoprompt']:
        st.text_area('Resultado do prompt do usuário', '''{promtpfinal}'''.format(promtpfinal=usaprompt()), label_visibility="visible", height=750)

if __name__ == '__main__':

    initialize_session_state()
    load_openai_key()
    startconvert()
    
        