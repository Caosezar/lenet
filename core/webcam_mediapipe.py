import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import time
import os

# Definições das nossas APIs Performáticas

class FacialRecognitionAPI:
    """
    Mock de uma API de Reconhecimento Facial.
    Na prática, receberia os landmarks (ou crop do rosto) e retornaria um ID único com base nas métricas faciais.
    """
    def __init__(self):
        # Aqui ficarão armazenados os "rostos" conhecidos
        self.known_faces = {}
    
    def identify(self, frame_rgb, face_landmarks) -> str:
        # Mock: Assumimos que a pessoa atual é sempre o "User 1".
        # Em uma implementação real, extrairíamos embeddings faciais usando bibliotecas específicas.
        return "Usuario Principal"

class ExpressionAPI:
    """
    API In-Memory Responsável por Registrar e Classificar as Expressões via Distância Euclidiana.
    Utiliza as 52 blendshapes (micro-expressões) calculadas de forma acelerada pela IA da Google.
    """
    def __init__(self):
        # Estrutura: { "User_ID": { "Label_da_Expressão": array_de_pesos_das_feições } }
        self.expressions = {}
        # Histórico leve de distância para suavizar inferência
        self.last_predicted = "Neutra (Sem Registro)"
    
    def register(self, user_id: str, label: str, blendshapes):
        if user_id not in self.expressions:
            self.expressions[user_id] = {}
        
        scores = [b.score for b in blendshapes]
        self.expressions[user_id][label] = np.array(scores)
        print(f"\n[API] Expressão '{label}' registrada com sucesso para {user_id}!")
        
    def predict(self, user_id: str, blendshapes) -> str:
        # Fallback 1: Extrai a característica nativa mais forte do MediaPipe (ex: 'mouthSmileLeft')
        active_features = [b for b in blendshapes if b.score > 0.45 and b.category_name not in ['_neutral', 'neutral']]
        fallback_label = "Auto: Neutro"
        if active_features:
            # Pega a top #1 feature que a pessoa está fazendo no momento
            top_b = sorted(active_features, key=lambda x: x.score, reverse=True)[0]
            fallback_label = f"MediaPipe: {top_b.category_name}"

        if user_id not in self.expressions or len(self.expressions[user_id]) == 0:
            return fallback_label
        
        # Converte a entrada atual para um vetor matemático de numpy
        current_features = np.array([b.score for b in blendshapes])
        
        best_label = "Desconhecida"
        min_distance = float('inf')
        
        # Compara as micro fisionomias (52 marcadores) da expressão com as gravadas
        for label, ref_features in self.expressions[user_id].items():
            dist = np.linalg.norm(current_features - ref_features)
            if dist < min_distance:
                min_distance = dist
                best_label = label
                
        # Limiar de semelhança da expressão
        if min_distance < 0.65:
            self.last_predicted = best_label
            return f"{best_label} (Gravada!)"
            
        return f"Procurando... | {fallback_label}"

# Utilitário para Design Responsivo no OpenCV (Usando JetBrains Mono)
def draw_text_jetbrains(cv2_im: np.ndarray, text: str, position: tuple, font_size: int = 24, color: tuple = (0, 255, 0)) -> np.ndarray:
    """
    Usamos o Pillow por baixo dos panos (ImageDraw + ImageFont) pra renderizar fontes elegantes
    diferentemente do padrão defasado cv2.putText.
    """
    cv2_im_rgb = cv2.cvtColor(cv2_im, cv2.COLOR_BGR2RGB)
    pil_im = Image.fromarray(cv2_im_rgb)
    
    draw = ImageDraw.Draw(pil_im)
    
    # Caminho onde nossa fonte premium foi baixada via script anterior
    font_path = os.path.join(os.path.dirname(__file__), "JetBrainsMono-Regular.ttf")
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()
        
    draw.text((position[0], position[1]), text, font=font, fill=color)
    return cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)

# Script principal da Aplicação
def main():
    face_api = FacialRecognitionAPI()
    expression_api = ExpressionAPI()
    
    # Setup da Mágica: MediaPipe FaceLandmarker
    BaseOptions = mp.tasks.BaseOptions
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    # Arquivo modelo offline hiper-performant que acabamos de baixar
    model_path = os.path.join(os.path.dirname(__file__), 'face_landmarker.task')
    
    # Configuração customizada para o nosso propósito de expressão:
    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.VIDEO,
        output_face_blendshapes=True, # Isso habilita nosso classificador de expressões (piscar, boca, etc)
        output_facial_transformation_matrixes=False,
        num_faces=1 # Limitado a 1 para extrema performance e foco
    )
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Erro ao tentar acessar a webcam. Verifique suas conexões e tente de novo.")
        return

    # Usamos o contexto 'with' gerenciado da lib do Google
    with FaceLandmarker.create_from_options(options) as landmarker:
        
        # Loop Performatizado "Em Tempo Real"
        while True:
            success, frame = cap.read()
            if not success:
                break
                
            frame = cv2.flip(frame, 1) # Torna o frame natural como um espelho de verdade
            h, w, _ = frame.shape
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            frame_timestamp_ms = int(time.time() * 1000)
            
            # Inferência base 
            result = landmarker.detect_for_video(mp_image, frame_timestamp_ms)
            
            current_user = None
            current_blendshapes = None
            text_x, text_y = 30, 30
            
            # Label Default se não houver ninguém em cena
            label_display = "Nenhum rosto detectado."
            
            if result.face_landmarks:
                landmarks = result.face_landmarks[0]
                
                # Calcular as coordenadas do Quadrado (Bounding Box) do rosto
                x_coords = [int(mark.x * w) for mark in landmarks]
                y_coords = [int(mark.y * h) for mark in landmarks]
                xmin, ymin = max(0, min(x_coords) - 10), max(0, min(y_coords) - 30)
                xmax, ymax = min(w, max(x_coords) + 10), min(h, max(y_coords) + 10)
                
                # Reposiciona o texto para logo acima do quadrado
                text_x = xmin
                text_y = ymin - 25
                
                # Desenha o Quadrado ao redor do rosto (Cor: Azul-esverdeado suave)
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (210, 230, 200), 1)
                
                # Pegar as 52 feições completas (com os nomes nativos inclusos)
                current_blendshapes = result.face_blendshapes[0]
                
                # Passo A: API identifica a pessoa
                current_user = face_api.identify(rgb_frame, landmarks)
                
                # Passo B: API classifica usando as features cadastradas e o fallback nativo
                detected_expr = expression_api.predict(current_user, current_blendshapes)
                label_display = f"[{current_user}] {detected_expr}"
                
                # Estilização Suave no Rosto (Pulando landmarks pra fps liso)
                for mark in landmarks[::5]: 
                    x = int(mark.x * w)
                    y = int(mark.y * h)
                    # Cor suavizada (branca-esverdeada platinada)
                    cv2.circle(frame, (x, y), 1, (200, 230, 200), -1)

            # --- RENDERIZAÇÃO NA TELA USANDO JETBRAINS MONO ---
            # Cor preta com offset (Sombra) e texto brilhante em cima pro design se destacar
            frame = draw_text_jetbrains(
                frame, 
                label_display, 
                position=(max(text_x+1, 10), max(text_y+1, 10)), 
                font_size=15, 
                color=(0, 0, 0)
            )
            frame = draw_text_jetbrains(
                frame, 
                label_display, 
                position=(max(text_x, 10), max(text_y, 10)), 
                font_size=15, 
                color=(255, 200, 0) # Gold Yellow neon
            )
            
            # Menu Minimalista na parte inferior
            menu_text1 = "Pressione [C] para Cadastrar"
            frame = draw_text_jetbrains(frame, menu_text1, position=(20, h - 70), font_size=16, color=(200, 200, 255))
            
            menu_text2 = "Pressione [Q] para Sair"
            frame = draw_text_jetbrains(frame, menu_text2, position=(20, h - 40), font_size=16, color=(200, 200, 255))
            
            cv2.imshow('Mediapipe Custom Expression API', frame)
            
            # Loop de Interatividade
            key = cv2.waitKey(5) & 0xFF
            if key == ord('q') or key == 27:
                break
                
            elif key == ord('c') or key == ord('C'):
                # O usuário pediu pra cadastrar, então abrimos o console e congelamos a imagem momentaneamente.
                if current_user and current_blendshapes:
                    print(f"\n--- PAUSA PARA CADASTRO DE UMA NOVA EXPRESSAO ---")
                    print(f"[{current_user}] Detectado!")
                    # Prompt no terminal para pegar a label
                    nova_label = input("-> Descreva que Expressao foi essa (ex: 'Sorrindo Feliz', 'Bravo'): ")
                    
                    if nova_label.strip():
                        expression_api.register(current_user, nova_label.strip(), current_blendshapes)
                    else:
                        print("[Aviso] Cancelado: Label Vazia.")
                        
                    print("--> Você ja pode voltar para a janela da Aplicação (Câmera).")
                else:
                    print("\n[Aviso] Você apertou [C] mas não tem ninguém na Câmera no momento.")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
