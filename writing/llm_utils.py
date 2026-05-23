import time


def invoke_with_retries(llm, prompt, attempts=3, delay_seconds=1):
    last_error = None

    for attempt in range(attempts):
        try:
            return llm.invoke(prompt).content.strip()
        except Exception as error:
            last_error = error

            if attempt == attempts - 1:
                break

            time.sleep(delay_seconds * (attempt + 1))

    raise last_error
