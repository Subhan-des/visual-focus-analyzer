import os
import numpy as np
import streamlit as st
import torch
from PIL import Image
import matplotlib.pyplot as plt
from scipy.ndimage import zoom
from scipy.special import logsumexp
import deepgaze_pytorch

st.set_page_config(page_title="Visual Focus Analyzer", layout="wide")
st.title("Visual Focus Analyzer")
st.caption("Developed by Subhan • v1.0")

os.makedirs("outputs", exist_ok=True)

@st.cache_resource
def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = deepgaze_pytorch.DeepGazeMSDB(pretrained=True).to(device)
    model.eval()
    return model, device

model, DEVICE = load_model()
st.write(f"Using device: {DEVICE}")

uploaded_file = st.file_uploader("Upload screenshot", type=["png", "jpg", "jpeg", "webp"])

max_width = st.slider("Max width", 800, 1800, 1400, 100)

if uploaded_file is not None:
    img = Image.open(uploaded_file).convert("RGB")
    img.thumbnail((max_width, max_width * 2))

    image = np.array(img)
    st.image(image, caption="Input image", use_container_width=True)

    image_tensor = torch.tensor(
        [image.transpose(2, 0, 1)],
        dtype=torch.float32
    ).to(DEVICE)

    centerbias_template = np.zeros((1024, 1024))
    cb_h, cb_w = centerbias_template.shape
    img_h, img_w, _ = image.shape

    centerbias = zoom(
        centerbias_template,
        (img_h / cb_h, img_w / cb_w),
        order=0
    )
    centerbias -= logsumexp(centerbias)

    centerbias_tensor = torch.tensor(
        [centerbias],
        dtype=torch.float32
    ).to(DEVICE)

    if st.button("Generate heatmap"):
        with st.spinner("Running DeepGaze..."):
            with torch.no_grad():
                log_density_prediction = model(
                    image_tensor,
                    centerbias_tensor,
                    pixel_per_dva=35.0,
                    dataset=None
                )

            prediction = np.squeeze(log_density_prediction.detach().cpu().numpy())
            saliency = np.exp(prediction)
            saliency = saliency / saliency.max()

            fig, ax = plt.subplots(figsize=(14, 8))
            ax.imshow(image)
            ax.imshow(saliency, alpha=0.5, cmap="jet")
            ax.axis("off")

            out_path = os.path.join("outputs", "deepgaze_heatmap.png")
            fig.savefig(out_path, bbox_inches="tight", pad_inches=0, dpi=200)

            st.pyplot(fig)

            with open(out_path, "rb") as f:
                st.download_button(
                    "Download heatmap",
                    f,
                    file_name="deepgaze_heatmap.png",
                    mime="image/png"
                )