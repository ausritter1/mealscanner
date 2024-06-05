import os
import streamlit as st
import base64
import requests
from PIL import Image
import io

# OpenAI API Key
api_key = os.getenv('OPENKEY')


# Function to encode the image
def encode_image(image):
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


# Function to get meal overview and calorie count using OpenAI API
def get_meal_info(image):
    base64_image = encode_image(image)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Identify the foods in this meal and estimate the total calorie count."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    return response.json()


# Streamlit app
def main():
    st.set_page_config(
        page_title="Meal Analyzer",
        page_icon="🍽️",
        layout="centered",
        initial_sidebar_state="auto",
    )

    # Custom CSS for better styling
    st.markdown("""
        <style>
        .reportview-container {
            background: #e0f7fa;
            padding: 2rem;
        }
        .sidebar .sidebar-content {
            background: #ffffff;
        }
        .main .block-container {
            max-width: 700px;
            margin: auto;
            padding: 2rem;
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🍽️ Meal Analyzer")
    st.write("Upload an image of your meal to get an overview and estimate the calorie count.")

    st.write("## Upload Your Meal Image")
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        st.write("")

        if st.button("Analyze Meal", use_container_width=True):
            with st.spinner("Analyzing..."):
                result = get_meal_info(image)

                try:
                    meal_info = result['choices'][0]['message']['content']
                    st.write("### Meal Overview:")
                    st.write(meal_info)
                except KeyError as e:
                    st.error("An error occurred while processing your image. Please try again.")


if __name__ == "__main__":
    main()
