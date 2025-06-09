from ai_interface import create_ai_interface

if __name__ == "__main__":
    # test_ai_interface()

    appkey = "sk-"
    ai = create_ai_interface(appkey)
    with  open("test.txt", "r") as f:
        git_analysis = f.read()
    ret = ai.generate_commit_message(git_analysis)
    print(ret)
