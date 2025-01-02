import streamlit as st
import time

def initialize_session_state():
    if 'stage' not in st.session_state:
        st.session_state.stage = 'init'
    if 'parameters' not in st.session_state:
        st.session_state.parameters = []
    if 'current_parameter' not in st.session_state:
        st.session_state.current_parameter = 0
    if 'counts' not in st.session_state:
        st.session_state.counts = {}
    if 'grand_total' not in st.session_state:
        st.session_state.grand_total = 0
    # Initialize parameters to start from 0
    for param in st.session_state.get('parameters', []):
        if f'current_count_{param}' not in st.session_state:
            st.session_state[f'current_count_{param}'] = 0

def reset_app():
    st.session_state.stage = 'init'
    st.session_state.parameters = []
    st.session_state.current_parameter = 0
    st.session_state.counts = {}
    st.session_state.grand_total = 0
    # Clear all counting states and totals
    for key in list(st.session_state.keys()):
        if key.startswith('current_count_') or key.startswith('total_'):
            del st.session_state[key]

def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def main():
    # Update the title styling
    st.markdown("""
        <style>
        .main-title {
            font-size: 3rem;
            font-weight: 600;
            color: #1f77b4;
            margin-bottom: 2rem;
            text-align: center;
        }
        .button-container {
            display: flex;
            justify-content: center;
            margin: 1rem 0;
        }
        .stButton > button {
            min-width: 200px;
            min-height: 60px;
            font-size: 1.2rem !important;
            margin: 0.5rem;
            border-radius: 10px;
        }
        .parameter-input {
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 15px;
            margin: 1rem 0;
        }
        .counter-display {
            font-size: 1.5rem !important;
            text-align: center;
            margin: 1rem 0 !important;
            padding: 1.5rem !important;
            background: #f8f9fa;
            border-radius: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .grand-total {
            background: linear-gradient(145deg, #28a745, #218838);
            color: white;
            padding: 2rem !important;
            border-radius: 15px;
            text-align: center;
            margin: 1.5rem 0 !important;
            font-size: 2rem !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .tap-button {
            width: min(80vw, 400px) !important;
            height: min(80vw, 400px) !important;
            border-radius: 50%;
            background: linear-gradient(145deg, #1f77b4, #2988cc);
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: min(10vw, 3rem) !important;
            cursor: pointer;
            margin: 2rem auto !important;
            transition: all 0.3s ease;
        }
        .tap-button:active {
            transform: scale(0.95);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .success-message {
            font-size: 1.5rem;
            color: #28a745;
            text-align: center;
            padding: 1rem;
            margin: 1rem 0;
        }
        .progress-section {
            margin: 2rem 0;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 15px;
        }
        .stProgress > div > div {
            height: 20px !important;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="main-title">Tap Counter App</h1>', unsafe_allow_html=True)
    initialize_session_state()

    # Make Start Over button more prominent
    col1, col2, col3 = st.columns([4, 4, 4])
    with col2:
        if st.button("🔄 Start Over", type="primary", key="start_over_top"):
            reset_app()
            st.rerun()
    
    st.divider()

    # Initial setup stage
    if st.session_state.stage == 'init':
        st.markdown('<div class="parameter-input">', unsafe_allow_html=True)
        num_parameters = st.number_input("How many parameters do you want to count?", 
                                       min_value=1, max_value=10, value=1,
                                       key="num_params")
        
        if num_parameters > 0:
            st.markdown("### Name your parameters")
            parameter_names = []
            for i in range(num_parameters):
                param_name = st.text_input(f"Parameter {i+1} name:", 
                                         value=f"Parameter {i+1}",
                                         key=f"param_name_{i}")
                parameter_names.append(param_name)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        if st.button("Continue", type="primary", key="continue_button"):
            st.session_state.stage = 'setup'
            st.session_state.parameters = parameter_names
            for param_name in parameter_names:
                st.session_state.counts[param_name] = 0
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Setup stage
    elif st.session_state.stage == 'setup':
        st.markdown('<div class="parameter-input">', unsafe_allow_html=True)
        st.markdown("### Set tap counts for each parameter")
        temp_counts = {}
        
        for param in st.session_state.parameters:
            count = st.number_input(f"How many taps for {param}?", 
                                  min_value=1, max_value=100, value=1,
                                  key=f"tap_count_{param}")
            temp_counts[param] = count
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        if st.button("Start Counting", type="primary"):
            st.session_state.counts = temp_counts
            st.session_state.stage = 'counting'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Counting stage
    elif st.session_state.stage == 'counting':
        if any(is_numeric(param) for param in st.session_state.parameters):
            st.markdown(f"""
                <div class="grand-total">
                    Grand Total: {st.session_state.grand_total}
                </div>
            """, unsafe_allow_html=True)

        if st.session_state.current_parameter < len(st.session_state.parameters):
            current_param = st.session_state.parameters[st.session_state.current_parameter]
            target_count = st.session_state.counts[current_param]
            
            # Initialize counts
            if f'current_count_{current_param}' not in st.session_state:
                st.session_state[f'current_count_{current_param}'] = 0
            if f'total_{current_param}' not in st.session_state:
                st.session_state[f'total_{current_param}'] = 0

            st.markdown(f"<h2 style='text-align: center; color: #1f77b4;'>{current_param}</h2>", 
                       unsafe_allow_html=True)

            # Display counters
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                    <div class="counter-display">
                        Taps: {st.session_state[f'current_count_{current_param}']} / {target_count}
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                remaining_taps = target_count - st.session_state[f'current_count_{current_param}']
                st.markdown(f"""
                    <div class="counter-display">
                        Remaining: {remaining_taps}
                    </div>
                """, unsafe_allow_html=True)

            # Display parameter total if numeric
            if is_numeric(current_param):
                st.markdown(f"""
                    <div class="counter-display" style="background: #e6f3ff;">
                        Parameter Total: {st.session_state[f'total_{current_param}']}
                    </div>
                """, unsafe_allow_html=True)

            # Control buttons
            col1, col2 = st.columns([1,2])
            with col1:
                if st.button("↺ Reset", key=f"reset_{current_param}", type="secondary"):
                    if is_numeric(current_param):
                        st.session_state.grand_total -= st.session_state[f'total_{current_param}']
                    st.session_state[f'current_count_{current_param}'] = 0
                    st.session_state[f'total_{current_param}'] = 0
                    st.rerun()

            with col2:
                if st.session_state[f'current_count_{current_param}'] < target_count:
                    if st.button("TAP", key=f"tap_{current_param}", type="primary"):
                        st.session_state[f'current_count_{current_param}'] += 1
                        if is_numeric(current_param):
                            param_value = float(current_param)
                            st.session_state[f'total_{current_param}'] += param_value
                            st.session_state.grand_total += param_value
                        if st.session_state[f'current_count_{current_param}'] >= target_count:
                            st.session_state.current_parameter += 1
                            if st.session_state.current_parameter >= len(st.session_state.parameters):
                                st.markdown('<div class="success-message">🎉 All parameters completed! 🎉</div>', 
                                          unsafe_allow_html=True)
                        st.rerun()
                else:
                    st.markdown('<div class="success-message">✅ Completed!</div>', 
                              unsafe_allow_html=True)
                    if st.button("Next →", key="next_param", type="primary"):
                        st.session_state[f'current_count_{current_param}'] = 0
                        st.session_state.current_parameter += 1
                        st.rerun()

            # Progress bar
            st.markdown('<div class="progress-section">', unsafe_allow_html=True)
            st.markdown("### Overall Progress")
            progress = st.session_state.current_parameter / len(st.session_state.parameters)
            st.progress(progress)
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
