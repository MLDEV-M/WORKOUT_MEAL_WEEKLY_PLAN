# Track Today's Exercises Page
def display_track_exercises_page(st):
    def fetch_exercises_from_supabase(supabase, selected_program):
        # Fetch exercises data for the selected program from Supabase
        response = supabase.table(selected_program).select('exercise_id', 'exercise_name_alternative').execute()
        
        # Check if the response contains any data
        if response.data:
            return response.data
        else:
            return []

    def my_form(exercises,selected_program, st, supabase):
        import pandas as pd
        #selected_program_exercise = str(selected_program) + '_exercise'
        #print('DSFSFq:',selected_program_exercise)
        # Fetch exercises for the given program
        #exercises = fetch_exercises_from_supabase(supabase, selected_program_exercise)
        program = pd.DataFrame(exercises)
        # Check if exercises were fetched
        if program.empty:
            st.write(f"No exercises found for {selected_program}")
            return [], []  # If no exercises found, return empty lists

        # Convert the fetched exercises into a DataFrame
        
        #st.write(f"Exercises for the {selected_program} program:")
        #st.write(program)

        # List of selected exercises to be returned
        ids_returned = []
        names_returned = []
        #completed_exercises = []  # List to store the completed exercises

        # User selects exercises from the current program
        with st.form(f"form_{selected_program}"):  # Ensure each form has a unique name
            st.write(f"Choose exercises from the {selected_program} program.")
            # directions for exercises
            if selected_program == "pylo":
                st.write(f"1 set -> 15 seconds rest -> Perform each repetition with maximum explosiveness, focusing on speed and power as in Taekwondo kicks.")
            if selected_program == "strength":
                st.write(f"1 set -> 90 seconds rest -> Focus on strong, controlled movements to build power and endurance for powerful Taekwondo strikes.")

            # Multiselect widget for exercise selection
            exercise_checked = st.multiselect(
                label='Which exercises did you complete?',
                options=program['exercise_name_alternative'].tolist(),
                help="Search and select exercises"
            )

            # Submit button for the form
            submitted = st.form_submit_button(f"Submit {selected_program}")
            
            if submitted:
                if exercise_checked:
                    st.write("You selected:")
                    for exercise in exercise_checked:
                        exercise_info = program[program['exercise_name_alternative'] == exercise]
                        st.write(f"- {exercise_info['exercise_name_alternative'].values[0]}")
                        ids_returned.append(exercise_info['exercise_id'].values[0])
                        names_returned.append(exercise_info['exercise_name_alternative'].values[0])
                        # Mark exercises as completed in the Supabase table
                        
                        update_exercise_tracking(supabase, exercise_info['exercise_id'].values[0], exercise_info['exercise_name_alternative'].values[0], st.session_state.user['user_id'])
                # After form submission
                        #completed_exercises.append(exercise_info['exercise_id'].values[0])
                    # Save the selected exercises to session_state
                    st.session_state.selected_exercises_ids = ids_returned
                    st.session_state.selected_exercises_names = names_returned
        return ids_returned, names_returned

    def get_uncompleted_exercises_for_week(weekday,supabase, st):
        from datetime import datetime, timedelta
        import pandas as pd

        # 2. Define current week range (Sunday to Saturday)
        today = datetime.now()

        # Calculate the start of the week (Sunday at 00:00)
        start_of_week = today - timedelta(days=today.weekday() + 1) if today.weekday() != 6 else today
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        print('sunday:',start_of_week)

        # Calculate the end of the week (Saturday at 23:59:59)
        end_of_week = start_of_week + timedelta(days=6)
        end_of_week = end_of_week.replace(hour=23, minute=59, second=59, microsecond=999999)
        print('saturday:',end_of_week)

        start_str = start_of_week.date().isoformat()
        end_str = end_of_week.date().isoformat()

        # 3. Get completed exercises from tracking table for current user and current week
        tracking_response = supabase.table("exercise_tracking").select("*").eq("user_id", st.session_state.user['user_id']).gte("completed_date", start_str).lte("completed_date", end_str).execute()
        completed_df = pd.DataFrame(tracking_response.data)

            

        if completed_df.empty:
            return []  # none completed, return all
        else:
            
            # manually remove stretch exercises
            stretch_list = [1001, 1002, 1003, 1004, 1005, 1006, 1007]  
            
            # Filter out the exercises that are completed on the given weekday
            completed_on_weekday = completed_df[completed_df['completed_week_day'] == weekday]
            
            # Filter out the stretch exercises that were completed on the given weekday
            completed_on_weekday_stretch = completed_on_weekday[completed_on_weekday['exercise_id'].isin(stretch_list)]
            st.write(list(completed_on_weekday_stretch['exercise_id'])) 
            # Now, remove these completed stretch exercises from the original completed_df
            remaining_exercises_df = completed_df[~completed_df['exercise_id'].isin(list(completed_on_weekday_stretch['exercise_id']))]
        
            # Return the remaining exercises as a list of exercise_ids
            return list(remaining_exercises_df["exercise_id"].unique())

    
    def unique_time_done_choose(day, st, supabase):
        import pandas as pd
    
        # Fetch exercises data from Supabase for the specific day
        response = supabase.table(day).select('exercise_id', 'exercise_name_alternative', 'primary_muschle_group', 'sets', 'repeats', 'repeats_type', 'table_name', 'reference_link', 'demo_time_done').execute()

        # IF response table is empty, return empty result
        if not response.data:
            return pd.DataFrame(), []
    
        start_program = pd.DataFrame(response.data)
        completed_ids = get_uncompleted_exercises_for_week(day,supabase, st)
        program = start_program[~start_program["exercise_id"].isin(completed_ids)]
        
        unique_time_done = list(program['demo_time_done'].unique())
        
        return program, unique_time_done

    
    def time_done_choose(day,time_done,start_program, st, supabase):
        import pandas as pd
        
        # Fetch exercises data from Supabase for the specific day
        #response = supabase.table(day).select('exercise_id', 'exercise_name_alternative','primary_muschle_group', 'sets', 'repeats', 'repeats_type', 'table_name','reference_link','demo_time_done').execute()
        # IF response table is empty
        #if not response.data:
        if start_program.empty:    
            return [], [], pd.DataFrame() 
            
        
        #start_program = pd.DataFrame(response.data)
        # choose only morning or only afternoon
        program_time = start_program[start_program["demo_time_done"]==time_done]
        # remove alredy complete exercises
        completed_ids = get_uncompleted_exercises_for_week(day,supabase, st)
        program = program_time[~program_time["exercise_id"].isin(completed_ids)]
    
        #st.write("All the exercises:")
        #st.write(program)
    
           
        # Check session state for existing selections
        if 'selected_exercises_ids' in st.session_state and 'selected_exercises_names' in st.session_state:
            ids_returned = st.session_state.selected_exercises_ids
            names_returned = st.session_state.selected_exercises_names
        else:
            ids_returned, names_returned = [], []
            
        # Get unique exercise categories (program names)
        unique_exercises = list(program['table_name'].unique())
        unique_exercises = unique_exercises[:4]  # Limit to 4 unique programs
    
        # Initialize empty lists for IDs and names of selected exercises
        ids_returned = []
        names_returned = []
        print('FDHGFD',unique_exercises)
        # Loop through each unique program and call the form for that program
        for program_i in unique_exercises:
            print('SDFGq: ',str(program_i))
            data_i = program[program['table_name']== str(program_i)]
            # Call the form function for the current unique program
            ids, names = my_form(data_i,program_i, st, supabase)
            st.write(f"[DEBUG] Program: {program_i}, IDs: {ids}, Names: {names}")
            # Append the returned IDs and names to the main lists
            ids_returned.extend(ids)
            names_returned.extend(names)
    
        # Return the final lists of selected exercise IDs and names
        return ids_returned, names_returned,program

    # Function to update the exercise tracking table in Supabase
    def update_exercise_tracking(supabase,exercise_id,exercise_name, user_choose):
        from datetime import date,datetime
        from zoneinfo import ZoneInfo
        # Get the current date
        today = date.today()
        #log the data to verify what we're trying to upsert
        print(f"Attempting to upsert exercise with ID: {exercise_id}, Name: {exercise_name}, User: {user_choose}, Date: {today}")
         # Ensure exercise_id is an integer
        exercise_id = int(exercise_id)
        # Check if the record already exists
        response_check = supabase.table('exercise_tracking').select('*').eq('user_id', user_choose).eq('exercise_id', exercise_id).eq('completed_date', today).execute()

        if response_check.data:
            # Update the record if it exists
            print(f"Record already exists: {response_check.data}")
        else:
            # Insert or update the exercise completion data in Supabase
            response = supabase.table(f'exercise_tracking').upsert({
                    'exercise_id': exercise_id,
                    'user_id': user_choose,  # Assuming you have a user ID in session_state
                    'completed_date': str(today),  # Add date of completion
                    'completed_week_day': datetime.now().strftime('%A') ,
                    'completed_time': datetime.now(ZoneInfo("Europe/Nicosia")).strftime("%H:%M")
                }
             # If exercise_id exists, update it
            ).execute()

            #if response.status_code == 200:
            #    st.success(f"Exercise {exercise_name} with ID {exercise_id} updated successfully!")
            #else:
            #    st.error(f"Error updating exercise {exercise_name}: {response.error_message}")



    from supabase import create_client, Client
    from datetime import datetime
    
    SUPABASE_URL = st.secrets["supabase"]["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["supabase"]["SUPABASE_KEY"]
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    

    # Define the days of the week in Greek
    exercise_day = ['ΔΕΥΤΕΡΑ', 'ΤΡΙΤΗ', 'ΤΕΤΑΡΤΗ', 'ΠΕΜΠΤΗ', 'ΠΑΡΑΣΚΕΥΗ', 'ΣΑΒΒΑΤΟ', 'ΚΥΡΙΑΚΗ']

    # Get the current day of the week in English
    today = datetime.now().strftime('%A')  # Get the day of the week in English (e.g., Monday, Tuesday, etc.)

    # Map the English day of the week to Greek
    day_translation = {
        'Monday': 'ΔΕΥΤΕΡΑ',
        'Tuesday': 'ΤΡΙΤΗ',
        'Wednesday': 'ΤΕΤΑΡΤΗ',
        'Thursday': 'ΠΕΜΠΤΗ',
        'Friday': 'ΠΑΡΑΣΚΕΥΗ',
        'Saturday': 'ΣΑΒΒΑΤΟ',
        'Sunday': 'ΚΥΡΙΑΚΗ'
    }

    # Get the Greek day for today
    today_in_greek = day_translation[today]

    # Create a selectbox with the default value set to today
    selected_program = st.selectbox(
        'Choose the day',
        options=exercise_day,
        index=exercise_day.index(today_in_greek),  # Set the default selection to today's day
        help="Select the day for the exercise program"
    )
    the_program,time_done_options = unique_time_done_choose(selected_program, st, supabase)
    if time_done_options:
        # Create a selectbox with the default value set to today
        selected_time_done = st.selectbox(
               'Choose the time of the day',
               options=time_done_options, #["MORNING","WORK BREAK","AFTERNOON","STRETCH"],  
               index=0,
               help="Select what time of the day you do for the exercise program"
            )
        st.write(f"Selected day and time: {selected_program} - {selected_time_done}")
        ids_choose, names_choose, plan = time_done_choose(selected_program,selected_time_done,the_program, st, supabase)
    
        
        user_choose =  st.session_state.user['user_id']
        
        
        # Final submit button to mark exercises as completed
        final_submit = st.button("Check Remain Exercises")
        if 'current_plan' not in st.session_state:
            st.session_state.current_plan = plan.copy()
        
        if final_submit:
            if not plan.empty:
                
                try:
                    #st.write("DEBUG: Submitted exercises", names_choose)
                    #st.write("DEBUG: For user ID", st.session_state.user['username'])
        
                    completed_ids = get_uncompleted_exercises_for_week(selected_program,supabase, st)
                    
                    plan = plan[~plan['exercise_id'].isin(list(completed_ids))]
                    st.session_state.current_plan = plan #plan[plan["table_name"]!="stretch"].copy() #KEEP STRETCH
                    st.write("Your remain exercises except stretches.",len(st.session_state.current_plan))
                    
                    st.write(st.session_state.current_plan)
                except Exception as e:
                    st.error("Please try again. Choose exercise completed!")
                    st.error(str(e))
            else: 
                st.write("Congratulations!!!") 
                st.write("You dont have remain exercises") 
    else:
        st.write("You dont have remain exercises") 


        



