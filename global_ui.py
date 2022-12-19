import streamlit as st


def setUI():
    st.markdown('''
<style>
.stApp header{
    display:none;
}
.streamlit-expanderHeader p{
	font-size: x-large;
}
.main .block-container{
    max-width: unset;
    padding-left: 5em;
    padding-right: 5em;
    padding-top: 0em;
    padding-bottom: 1em;
    }
[data-testid="stMetricDelta"] > div:nth-child(2){
    justify-content: center;
}
</style>
''', unsafe_allow_html=True)

def setTransition():
    st.markdown('''
<style>
@keyframes append-animate2 {
	from {
		transform: scale(0);
		opacity: 0;
	}
	to {
		transform: scale(1);
		opacity: 1;	
	}
}
@keyframes append-animate {
	from {
		transform: scaleY(0);
		opacity: 0;
	}
	to {
		transform: scaleY(1);
		opacity: 1;
	}
}

.element-container {
	transform-origin: 50% 0;
	animation: append-animate .6s linear;
}
</style>
''', unsafe_allow_html=True)
