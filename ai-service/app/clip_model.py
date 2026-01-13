from PIL import Image
import torch
import clip

device = "cuda" if torch.cuda.is_available() else "cpu"

model, preprocess = clip.load("ViT-B/32", device=device)

def encode_image(image_path: str):
    """Возвращает эмбеддинг картинки"""
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        embedding = model.encode_image(image)
        embedding /= embedding.norm(dim=-1, keepdim=True)
    return embedding

def similarity_score(img_emb1, img_emb2):
    """Косинусное сходство"""
    return (img_emb1 @ img_emb2.T).item()
