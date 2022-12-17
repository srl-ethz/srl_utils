# SRL Shared Utilities

Here is a repo for shared utils. How do you know if something should be a shared util? Well, if you need to use a function in more than one context, there is a good chance it might benefit someone else as well.

As much as we want to grow this repo, and have people contribute, we also need to have in place some quality metrics for code and documentation to ensure that it remains usable. Ideally, these practices would eventually spread to other repos as well :)

## Making contributions

First of all, thank you for considering making a contribution! We understand this takes additional effort on your part and may not come with immediate gains, and is there greatly appreciated.

Now, logistics. Since we want to have this repo be usable by many people, we need to adhere to some code quality standards. But don't worry you will receive help in every step of the way. To make this easy to follow, we use pre-commit hooks that can be run by anyone. This will run a series of code quality checks on your new code and let you know if there are violations (and even fix some of those for you!).

How do you run these pre-commit hooks? Well, that's easy! If you installed the requirements specified in `requirements.txt` you already have `pre-commit` installed. All you need to do is, before you commit your code, navigate to your repo and run
```shell
pre-commit run
```

⚠️ If you are running this for the first time, it will take a few minutes to set up the environment.

That's it! Well, that should run all the hooks and show you what needs to be changed. This will also format your code to match the standards we have setup.

What if you have already made commits without running the hooks? Just run teh hooks on all files in the repo like this:
```shell
pre-commit run --all
```

We understand this process isn't a lot of fun at the beginning, especially because some of the these checkers can be quite nit-picky.However, these tools help ensure that we follow a unified standard, and once you get used to these tools, you will flinch at the sight of poorly formatted / not properly documented code and will likely want to setup these tools yourself in every repo :)
