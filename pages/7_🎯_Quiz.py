"""Short educational quiz for the EcoWatt event."""
import streamlit as st

from ecowatt.services.quiz_service import Quiz, QuizQuestion, QuizService
from ecowatt.utils.logging import track_event
from ecowatt.utils.session import init_session_state
from ecowatt.utils.features import feature_enabled

st.set_page_config(page_title="Quiz — EcoWatt", page_icon="🎯", layout="centered")
init_session_state()
track_event("page_view", page="quiz")

if not feature_enabled("event_quiz", True):
    st.info("O quiz esta desativado para este evento.")
    st.stop()

quiz = Quiz(
    id="ecowatt-basics",
    title="Desafio EcoWatt",
    questions=[
        QuizQuestion("power-energy", "O que o kWh mede?", ("Energia consumida", "Potencia instantanea", "Tensao"), 0, "kWh combina potencia e tempo para representar energia consumida."),
        QuizQuestion("power-unit", "Qual unidade mede potencia?", ("Watt (W)", "Quilowatt-hora (kWh)", "Litro"), 0, "Watt mede a potencia instantanea de um aparelho."),
        QuizQuestion("standby", "O que ajuda a reduzir consumo em stand-by?", ("Desligar da tomada", "Aumentar o brilho", "Deixar a luz acesa"), 0, "Retirar aparelhos da tomada evita o consumo quando eles nao estao em uso."),
    ],
    enabled=True,
    reward_enabled=False,
)

if "quiz_service" not in st.session_state:
    st.session_state.quiz_service = QuizService()
service: QuizService = st.session_state.quiz_service
attempt = service.start(quiz, st.session_state.analytics_session_started and st.session_state.user_id)

st.title(quiz.title)
st.caption("Responda para revisar conceitos de energia. O resultado e educativo e nao representa uma competicao oficial.")

if attempt.score is None:
    progress = len(attempt.answers) / len(quiz.questions)
    st.progress(progress, text=f"Progresso: {len(attempt.answers)}/{len(quiz.questions)}")
    question_by_id = {question.id: question for question in quiz.questions}
    for question_id in attempt.question_ids:
        question = question_by_id[question_id]
        selected = st.radio(question.prompt, question.options, index=None, key=f"quiz_{question.id}")
        if selected is not None:
            option_index = question.options.index(selected)
            service.answer(quiz, attempt, question.id, option_index)
            st.caption(question.explanation)
    if len(attempt.answers) == len(quiz.questions) and st.button("Finalizar quiz", type="primary"):
        service.finish(quiz, attempt)
        track_event("quiz_completed", score=attempt.score)
        st.rerun()
else:
    st.success(f"Resultado: {attempt.score}/{len(quiz.questions)} acertos")
    for result in service.result(quiz, attempt):
        st.write(("Acertou" if result["correct"] else "Revise") + ": " + str(result["explanation"]))
    if attempt.participation_code:
        st.info(f"Codigo simbolico de participacao: {attempt.participation_code}")
