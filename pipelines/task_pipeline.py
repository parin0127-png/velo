from agents.intake_agent import intake_agent
from agents.planner_agent import planner
from agents.executor_agent import executor
from agents.memory_agent import compact_memory, save_memory, get_memory
from agents.critic_agent import critic, save_lesson, get_lesson
from db.model import create_tables, save_task

def run_task(user_input, session_id = "default"):
    print("> VELO is starting...........")
    total_tokens = 0
    task_type = ""
    
    try : 
        create_tables()

        print("> [Intake Agent]")
        intake_result , tokens = intake_agent(user_input)
        total_tokens += tokens["total"]
        print(intake_result)

        entities = ""
        task_type = ""
        for line in intake_result.split("\n"):
            if line.startswith("entities:"):
                entities = line.replace("entities:" , "").strip()
            if line.startswith("task_type:"):
                task_type = line.replace("task_type:" , "").strip()
        lessons = get_lesson()
    except Exception as e:
        print(f"> [Intake Agent Failed]: {e}")
        return

    try : 

        print("> [Planner Agent]")
        plan_input = intake_result
        if lessons:
            plan_input += f"\n\nPast lessons to keep in mind:\n{lessons}"
        plan_result , tokens = planner(plan_input)
        total_tokens += tokens["total"]
        print(plan_result)

    except Exception as e:
        print(f"> [Planner Agent Failed]: {e}")
        return

    try:

        print("> [Executor Agent]")
        execute_result , tokens = executor(plan_result, entities, task_type, user_input)
        total_tokens += tokens["total"]
        print(execute_result)

    except Exception as e:
        print(f"> [Executor Agent Failed]: {e}")
        return


    try: 
        print("> [Critic Agent]")
        critic_result , tokens = critic(user_input, execute_result)
        total_tokens += tokens["total"]
        print(critic_result)

        for line in critic_result.split("\n"):
            if line.startswith("lesson:") and "none" not in line :
                lesson = line.replace("lesson:" , "").strip()
                save_lesson(lesson)
    except Exception as e:
        print(f"> [Critic Agent Failed]: {e}")
    

    try:

        full_conversation = f"User: {user_input} \n {intake_result} \n {plan_result} \n {execute_result}"
        summary = compact_memory(full_conversation)
        save_memory(session_id , summary)
        save_task(user_input, task_type, execute_result)

    except Exception as e:
        print(f"> [Memory Failed]: {e}")

    print(f"\n--- DONE | Total tokens used: {total_tokens} ---")
    return execute_result