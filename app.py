import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title='Diet & Workout Planner', page_icon='💪', layout='wide')

@st.cache_resource
def load_models():
    return joblib.load('fitness_models.pkl')

models = load_models()

st.title('💪 AI-Powered Diet & Workout Planner')
st.caption('Enter your details in the sidebar and click Get Plan.')

with st.sidebar:
    st.header('Your Details')
    sex = st.radio('Sex', ['Male', 'Female'], horizontal=True)
    age = st.slider('Age', 10, 90, 25)

    unit = st.radio('Height unit', ['cm', 'meter', 'feet'], horizontal=True)

    if unit == 'cm':
        height_cm = st.number_input('Height (cm)', 120.0, 220.0, 152.0)
    elif unit == 'meter':
        height_m = st.number_input('Height (meter)', 1.20, 2.20, 1.52, step=0.01)
        height_cm = height_m * 100
    else:
        ft_text = st.text_input('Height (feet.inch)', '5.0',
                                help='5.1 means 5 feet 1 inch, 5.10 means 5 feet 10 inch')
        try:
            parts = ft_text.strip().split('.')
            f = int(parts[0])
            i = int(parts[1]) if len(parts) > 1 and parts[1] != '' else 0
            if not (4 <= f <= 7) or not (0 <= i <= 11):
                raise ValueError
            height_cm = f * 30.48 + i * 2.54
        except ValueError:
            st.error('Type feet like 5.1 (5 ft 1 in). Inches must be 0 to 11.')
            st.stop()


    weight = st.number_input('Weight (kg)', 30.0, 200.0, 55.0)
    hyp = st.radio('Hypertension', ['No', 'Yes'], horizontal=True)
    dia = st.radio('Diabetes', ['No', 'Yes'], horizontal=True)
    go = st.button('Get Plan', type='primary', use_container_width=True)

if go:
    height = height_cm / 100
    bmi = round(weight / height**2, 2)

    if bmi < 18.5:
        level = 'Underweight'
    elif bmi < 25:
        level = 'Normal'
    elif bmi < 30:
        level = 'Overweight'
    else:
        level = 'Obese'
    goal = 'Weight Gain' if level in ['Underweight', 'Normal'] else 'Weight Loss'

    row = pd.DataFrame([{
        'Age': age, 'Height': height, 'Weight': weight, 'BMI': bmi,
        'Level': level,
        'Sex': 1 if sex == 'Male' else 0,
        'Hypertension': 1 if hyp == 'Yes' else 0,
        'Diabetes': 1 if dia == 'Yes' else 0,
        'Fitness Goal': goal
    }])

    c1, c2, c3 = st.columns(3)
    c1.metric('BMI', bmi)
    c2.metric('Category', level)
    c3.metric('Goal', goal)

    tab1, tab2, tab3 = st.tabs(['🏋️ Exercises', '🛠️ Equipment', '🥗 Diet'])
    with tab1:
        st.success(models['Exercises'].predict(row)[0])
    with tab2:
        st.info(models['Equipment'].predict(row)[0])
    with tab3:
        st.warning(models['Diet'].predict(row)[0])

    st.caption('This is a student project and not medical advice. Please consult a doctor or dietitian.')
else:
    st.info('👈 Fill in your details in the sidebar and click **Get Plan**.')
