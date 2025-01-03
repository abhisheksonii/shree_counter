import streamlit as st
import time
import json
import datetime
import os

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
    if 'saved_sessions' not in st.session_state:
        st.session_state.saved_sessions = {}
        load_sessions_from_file()
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    if 'editing_session' not in st.session_state:
        st.session_state.editing_session = None
    # Initialize parameters to start from 0
    for param in st.session_state.get('parameters', []):
        if f'current_count_{param}' not in st.session_state:
            st.session_state[f'current_count_{param}'] = 0

def reset_app():
    # Reset everything including grand total
    st.session_state.grand_total = 0
    st.session_state.current_parameter = 0
    # Clear all counting states and totals
    for param in st.session_state.parameters:
        st.session_state[f'current_count_{param}'] = 0
        st.session_state[f'total_{param}'] = 0

def clear_current_counts():
    # Only reset current counts, keep the grand total
    st.session_state.current_parameter = 0
    for param in st.session_state.parameters:
        st.session_state[f'current_count_{param}'] = 0
        st.session_state[f'total_{param}'] = 0

def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def save_session():
    session_data = {
        'parameters': st.session_state.parameters,
        'counts': st.session_state.counts,
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'grand_total': st.session_state.grand_total
    }
    
    # Get existing sessions
    if 'saved_sessions' not in st.session_state:
        st.session_state.saved_sessions = {}
    
    # Ask for session name
    session_name = st.text_input("Enter a name for this session:", key="session_name")
    if session_name and st.button("Save Session"):
        st.session_state.saved_sessions[session_name] = session_data
        st.success(f"Session '{session_name}' saved successfully!")

def load_session():
    if 'saved_sessions' not in st.session_state or not st.session_state.saved_sessions:
        st.warning("No saved sessions found.")
        return False
    
    session_name = st.selectbox(
        "Select a session to load:",
        options=list(st.session_state.saved_sessions.keys()),
        key="session_select"
    )
    
    session_data = st.session_state.saved_sessions[session_name]
    
    # Create columns for the two loading options
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Load Without Changes"):
            st.session_state.parameters = session_data['parameters']
            st.session_state.counts = session_data['counts']
            st.session_state.grand_total = session_data.get('grand_total', 0)
            st.session_state.stage = 'counting'
            st.session_state.current_parameter = 0
            # Initialize counts for the loaded parameters
            for param in st.session_state.parameters:
                st.session_state[f'current_count_{param}'] = 0
                st.session_state[f'total_{param}'] = 0
            st.success(f"Session '{session_name}' loaded successfully!")
            return True
    
    with col2:
        if st.button("Edit Parameters"):
            st.session_state.edit_mode = True
            st.session_state.editing_session = session_name
            return False
    
    # Show edit interface only if edit mode is active
    if st.session_state.get('edit_mode', False) and st.session_state.get('editing_session') == session_name:
        st.markdown("### Edit Parameters")
        edited_parameters = []
        edited_counts = {}
        
        for i, param in enumerate(session_data['parameters']):
            # Allow editing parameter name
            new_param = st.text_input(
                f"Parameter {i+1}:",
                value=param,
                key=f"edit_param_{i}"
            )
            # Allow editing tap count
            new_count = st.number_input(
                f"Taps for {new_param}:",
                min_value=1,
                value=session_data['counts'][param],
                key=f"edit_count_{i}"
            )
            edited_parameters.append(new_param)
            edited_counts[new_param] = new_count
        
        if st.button("Confirm Changes"):
            st.session_state.parameters = edited_parameters
            st.session_state.counts = edited_counts
            st.session_state.grand_total = session_data.get('grand_total', 0)
            st.session_state.stage = 'counting'
            st.session_state.current_parameter = 0
            # Initialize counts for the loaded parameters
            for param in st.session_state.parameters:
                st.session_state[f'current_count_{param}'] = 0
                st.session_state[f'total_{param}'] = 0
            # Clear edit mode
            st.session_state.edit_mode = False
            st.session_state.editing_session = None
            st.success(f"Session '{session_name}' loaded and updated successfully!")
            return True
            
    return False

def delete_session():
    if 'saved_sessions' not in st.session_state or not st.session_state.saved_sessions:
        st.warning("No saved sessions to delete.")
        return
    
    session_to_delete = st.selectbox(
        "Select a session to delete:",
        options=list(st.session_state.saved_sessions.keys()),
        key="session_delete"
    )
    
    if st.button("Delete Selected Session"):
        del st.session_state.saved_sessions[session_to_delete]
        st.success(f"Session '{session_to_delete}' deleted successfully!")

def save_sessions_to_file():
    try:
        sessions_data = {
            name: {
                'parameters': data['parameters'],
                'counts': data['counts'],
                'timestamp': data['timestamp'],
                'grand_total': data.get('grand_total', 0)
            }
            for name, data in st.session_state.saved_sessions.items()
        }
        
        with open('saved_sessions.json', 'w') as f:
            json.dump(sessions_data, f)
    except Exception as e:
        st.error(f"Error saving sessions: {str(e)}")

def load_sessions_from_file():
    try:
        if os.path.exists('saved_sessions.json'):
            with open('saved_sessions.json', 'r') as f:
                st.session_state.saved_sessions = json.load(f)
    except Exception as e:
        st.warning(f"Could not load saved sessions: {str(e)}")
        st.session_state.saved_sessions = {}

def main():
    # Update the title and styling - removing unnecessary card styles
    st.markdown("""
        <style>
        .main-title {
            font-size: 2.5rem;
            font-weight: 600;
            color: #1f77b4;
            margin-bottom: 1rem;
            text-align: center;
        }
        .stButton > button {
            width: 100%;
            font-size: 1.2rem !important;
            margin: 0.25rem 0;
            border-radius: 10px;
        }
        .counter-display {
            font-size: 1.5rem !important;
            text-align: center;
            margin: 0.5rem 0 !important;
        }
        .grand-total {
            background: linear-gradient(145deg, #28a745, #218838);
            color: white;
            padding: 1rem !important;
            border-radius: 15px;
            text-align: center;
            margin: 0.5rem 0 !important;
            font-size: 2rem !important;
        }
        .tap-button {
            width: 100% !important;
            height: 150px !important;
            background: linear-gradient(145deg, #1f77b4, #2988cc);
            color: white;
            font-size: 2rem !important;
            margin: 0.5rem 0 !important;
        }
        .success-message {
            font-size: 1.5rem;
            color: #28a745;
            text-align: center;
            padding: 0.5rem;
            margin: 0.5rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="main-title">Tap Counter App</h1>', unsafe_allow_html=True)
    initialize_session_state()

    # Make Start Over button more compact
    if st.button("🔄 Start Over", type="primary", key="start_over_top"):
        st.session_state.stage = 'init'  # This will restart the entire app
        st.session_state.parameters = []
        st.session_state.counts = {}
        st.session_state.grand_total = 0
        # Clear all counting states and totals
        for key in list(st.session_state.keys()):
            if key.startswith('current_count_') or key.startswith('total_'):
                del st.session_state[key]
        st.rerun()

    # Initial setup stage
    if st.session_state.stage == 'init':
        num_parameters = st.number_input("How many parameters do you want to count?", 
                                       min_value=1, value=1,
                                       key="num_params")
        
        if num_parameters > 0:
            st.markdown("### Name your parameters")
            parameter_names = []
            for i in range(num_parameters):
                param_name = st.text_input(f"Parameter {i+1} name:", 
                                         value="",
                                         placeholder=f"Enter parameter {i+1} name",
                                         key=f"param_name_{i}")
                if param_name:
                    parameter_names.append(param_name)
                else:
                    parameter_names.append(f"Parameter {i+1}")

        if st.button("Continue", type="primary", key="continue_button"):
            st.session_state.stage = 'setup'
            st.session_state.parameters = parameter_names
            for param_name in parameter_names:
                st.session_state.counts[param_name] = 0
            st.rerun()

    # Setup stage
    elif st.session_state.stage == 'setup':
        st.markdown("### Set tap counts for each parameter")
        temp_counts = {}
        
        for param in st.session_state.parameters:
            count = st.number_input(f"How many taps for {param}?", 
                                  min_value=1, value=1,
                                  key=f"tap_count_{param}")
            temp_counts[param] = count

        if st.button("Start Counting", type="primary"):
            st.session_state.counts = temp_counts
            st.session_state.stage = 'counting'
            st.rerun()

    # Counting stage
    elif st.session_state.stage == 'counting':
        # Display grand total if any numeric parameters exist
        if any(is_numeric(param) for param in st.session_state.parameters):
            st.markdown(f"""
                <div class="grand-total">
                    Grand Total: {st.session_state.grand_total}
                </div>
            """, unsafe_allow_html=True)

        # Check if we've completed all parameters
        if st.session_state.current_parameter >= len(st.session_state.parameters):
            st.session_state.current_parameter = len(st.session_state.parameters) - 1  # Stay on last parameter
        
        current_param = st.session_state.parameters[st.session_state.current_parameter]
        target_count = st.session_state.counts[current_param]
        
        # Initialize counts if not present
        if f'current_count_{current_param}' not in st.session_state:
            st.session_state[f'current_count_{current_param}'] = 0
        if f'total_{current_param}' not in st.session_state:
            st.session_state[f'total_{current_param}'] = 0

        st.markdown(f"<h2 style='text-align: center; color: #1f77b4;'>{current_param}</h2>", 
                   unsafe_allow_html=True)

        # TAP button
        if st.session_state[f'current_count_{current_param}'] < target_count:
            if st.button("TAP", key=f"tap_{current_param}", type="primary", use_container_width=True):
                st.session_state[f'current_count_{current_param}'] += 1
                if is_numeric(current_param):
                    param_value = float(current_param)
                    st.session_state[f'total_{current_param}'] += param_value
                    st.session_state.grand_total += param_value
                if st.session_state[f'current_count_{current_param}'] >= target_count:
                    if st.session_state.current_parameter < len(st.session_state.parameters) - 1:
                        st.session_state.current_parameter += 1
                st.rerun()
        else:
            st.markdown('<div class="success-message">✅ Completed!</div>', 
                      unsafe_allow_html=True)
            if st.session_state.current_parameter < len(st.session_state.parameters) - 1:
                if st.button("Next →", key="next_param", type="primary"):
                    st.session_state.current_parameter += 1
                    st.rerun()

        # Control buttons below TAP button
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Clear All", key="clear_all"):
                clear_current_counts()
                st.rerun()
        
        with col2:
            if st.button("↺ Reset", key=f"reset_{current_param}", type="secondary"):
                reset_app()  # Use the reset_app function instead of individual resets
                st.rerun()

    # Add Session Management UI
    with st.expander("Session Management"):
        tab1, tab2, tab3 = st.tabs(["Load Session", "Save Session", "Delete Session"])
        
        with tab1:
            if load_session():
                save_sessions_to_file()
                st.rerun()
        
        with tab2:
            if st.session_state.stage == 'counting':
                if save_session():
                    save_sessions_to_file()
            else:
                st.info("Complete the setup to save the session.")
        
        with tab3:
            if delete_session():
                save_sessions_to_file()

if __name__ == "__main__":
    main()
