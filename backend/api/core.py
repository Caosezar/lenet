"""Core AI logic for facial recognition and expression detection"""

import numpy as np
import time


class FacialRecognitionAPI:
    """
    Mock API for facial recognition.
    In production, would use face embedding models.
    """
    def __init__(self):
        self.known_faces = {}
    
    def identify(self, face_landmarks) -> str:
        """Mock identification - always returns hardcoded user"""
        return "Usuario Principal"


class ExpressionAPI:
    """
    In-memory expression registration and classification API.
    Uses 52 blendshapes from MediaPipe FaceLandmarker for recognition.
    """
    def __init__(self):
        # Structure: { "User_ID": { "Label_da_Expressão": array_de_pesos_das_feições } }
        self.expressions: dict = {}
        self.last_predicted = "Neutra (Sem Registro)"
    
    def register(self, user_id: str, label: str, blendshapes: list) -> dict:
        """
        Register a new expression for a user.
        
        Args:
            user_id: User identifier
            label: Expression label (e.g., "Sorrindo")
            blendshapes: List of dicts with 'category_name' and 'score'
        
        Returns:
            Dict with success status and message
        """
        if user_id not in self.expressions:
            self.expressions[user_id] = {}
        
        scores = [b.get("score", 0) for b in blendshapes]
        self.expressions[user_id][label] = np.array(scores)
        
        return {
            "success": True,
            "message": f"Expression '{label}' registered successfully for {user_id}",
            "user_id": user_id,
            "label": label
        }
    
    def predict(self, user_id: str, blendshapes: list) -> dict:
        """
        Predict expression from blendshapes.
        
        Args:
            user_id: User identifier
            blendshapes: List of dicts with 'category_name' and 'score'
        
        Returns:
            Dict with predicted expression, confidence, and top blendshapes
        """
        current_features = np.array([b.get("score", 0) for b in blendshapes])
        
        # Fallback: find the strongest native feature
        blendshape_scores = [(b.get("category_name", "unknown"), b.get("score", 0)) for b in blendshapes]
        top_fallback = sorted(blendshape_scores, key=lambda x: x[1], reverse=True)[:5]
        
        best_fallback_label = "Auto: Neutro"
        if top_fallback and top_fallback[0][1] > 0.45:
            best_fallback_label = f"MediaPipe: {top_fallback[0][0]}"
        
        # If no expressions registered, return fallback
        if user_id not in self.expressions or len(self.expressions[user_id]) == 0:
            return {
                "expression": best_fallback_label,
                "confidence": 0.0,
                "top_blendshapes": [{"name": name, "score": score} for name, score in top_fallback[:5]]
            }
        
        # Compare with registered expressions using Euclidean distance
        best_label = "Desconhecida"
        min_distance = float('inf')
        
        for label, ref_features in self.expressions[user_id].items():
            dist = np.linalg.norm(current_features - ref_features)
            if dist < min_distance:
                min_distance = dist
                best_label = label
        
        # Confidence threshold: if distance is low (similar), high confidence
        confidence = 0.0
        expression_result = f"Procurando... | {best_fallback_label}"
        
        if min_distance < 0.65:
            # Map distance to confidence (lower distance = higher confidence)
            confidence = max(0, 100 * (1 - (min_distance / 0.65)))
            expression_result = f"{best_label} (Gravada!)"
            self.last_predicted = best_label
        
        return {
            "expression": expression_result,
            "confidence": confidence,
            "top_blendshapes": [{"name": name, "score": score} for name, score in top_fallback[:5]]
        }
