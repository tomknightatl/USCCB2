The Definitive Guide to Managing Gemini CLI (v0.2.2): Using a .env file and /auth
This guide provides the complete, intended workflow for managing authentication in the Gemini CLI. It allows you to start on the free tier and seamlessly switch to a paid API key when you hit a quota limit, all without losing your conversation context.

Part 1: The Setup (One-Time Action)
You need to create a .env file in your project directory to securely store your API key. The Gemini CLI will automatically find and use this file when instructed.
What is a .env file?
A .env file is a standard way to manage environment variables for a specific project. It allows you to keep your secret keys out of your code and makes it easy to switch configurations.
Step 1: Create the .env File
Open your terminal and navigate (cd) to your project's root directory.
Run the following command to create the file and add your key. Be sure to replace YOUR_API_KEY with your actual key from AI Studio.
Bash
echo 'GEMINI_API_KEY="YOUR_API_KEY"' > .env


Step 2: Secure Your Key (Crucial)
You must prevent your .env file from ever being committed to version control (like Git).
Run this command to add .env to your project's .gitignore file. If you don't have a .gitignore file, this command will create one.
Bash
echo '.env' >> .gitignore


Your one-time setup is now complete for this project.

Part 2: The Workflow: Switching Tiers Live
Here is the simple, intended process for when you hit your free-tier quota.
You are in an interactive session (gemini -i) in your project directory and see the Quota exceeded... error. Do not quit the session.
In the gemini> prompt, simply run the /auth command:
/auth


The Gemini CLI will automatically detect and load the GEMINI_API_KEY from the .env file in your current directory. It will switch your session to the paid tier.
Continue your conversation. Your chat history is fully preserved. You can now resubmit your last prompt, and it will work.

Part 3: Switching Back to the Free Tier
How you switch back depends on your needs:
Easiest Method (End Session): Simply quit the session with Ctrl+C. The next time you run gemini -i from within this project directory, it will automatically read the .env file and start you on the paid tier.
To Use the Free Tier in the Same Project: Temporarily rename your .env file.
Bash
mv .env .env.bak

Now, when you run gemini -i or /auth, the key will not be found, and you will use the free tier. Rename it back (mv .env.bak .env) to switch again.
To Use the Free Tier in a Different Project: Simply cd to a different directory that does not have a .env file and run gemini -i. You will be on the free tier by default.

