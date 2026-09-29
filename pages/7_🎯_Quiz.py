"""Short educational quiz for the EcoWatt event."""
import streamlit as st

from ecowatt.services.quiz_service import (
    PERSISTED_QUIZ_ID,
    QuizPersistenceUnavailable,
    QuizService,
    SupabaseQuizRepository,
)
from ecowatt.utils.logging import track_event
from ecowatt.utils.session import init_session_state
from ecowatt.utils.features import feature_enabled

st.set_page_config(page_title="Quiz — EcoWatt", page_icon="🎯", layout="centered")
init_session_state()
track_event("page_view", page="quiz")

if not feature_enabled("event_quiz", True):
    st.info("O quiz esta desativado para este evento.")
    st.stop()

if "quiz_service" not in st.session_state:
    st.session_state.quiz_service = QuizService(repository=SupabaseQuizRepository())
service: QuizService = st.session_state.quiz_service
try:
    quiz = service.repository.load_quiz(PERSISTED_QUIZ_ID)
    attempt = service.start(
        quiz,
        st.session_state.analytics_session_id,
        st.session_state.participant_id,
    )
except ValueError as exc:
    st.info(str(exc))
    st.stop()
except QuizPersistenceUnavailable as exc:
    st.error(str(exc))
    st.stop()

st.title(quiz.title)
st.caption("Responda para revisar conceitos de energia. O resultado e educativo e nao representa uma competicao oficial.")

if attempt.score is None:
    question_count = len(attempt.question_ids)
    progress = len(attempt.answers) / question_count
    st.progress(progress, text=f"Progresso: {len(attempt.answers)}/{question_count}")
    question_by_id = {question.id: question for question in quiz.questions}
    for question_id in attempt.question_ids:
        question = question_by_id[question_id]
        selected = st.radio(question.prompt, question.options, index=None, key=f"quiz_{question.id}")
        if selected is not None:
            option_index = question.options.index(selected)
            service.answer(quiz, attempt, question.id, option_index)
    if len(attempt.answers) == len(quiz.questions) and st.button("Finalizar quiz", type="primary"):
        service.finish(quiz, attempt)
        track_event("quiz_completed", score=attempt.score)
        st.rerun()
else:
    st.success(f"Resultado: {attempt.score}/{len(quiz.questions)} acertos")
    st.markdown("### Revisão das respostas")
    for result in service.result(quiz, attempt):
        with st.container(border=True):
            if result["correct"]:
                st.success(f"✓ Acertou: {result['prompt']}")
            else:
                st.error(f"✗ Errou: {result['prompt']}")
                st.markdown(f"**Resposta correta:** {result['correct_answer']}")
            st.write(result["explanation"])
    if attempt.participation_code:
        st.info(f"Codigo simbolico de participacao: {attempt.participation_code}")
