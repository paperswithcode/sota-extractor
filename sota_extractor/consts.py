import os
import enum


DEBUG = os.environ.get("SOTA_EXTRACTOR_DEBUG", "false").lower() == "true"


class Format(str, enum.Enum):
    """Output format.

    At the moment only supported format is JSON, but in the future YAML support
    is planned.
    """

    json = "json"
    json_gz = "json.gz"


NLP_PROGRESS_REPO = "https://github.com/sebastianruder/NLP-progress"


EFF_TASK_CONVERSION = dict(
    [
        ("Detection of Instrumentals musical tracks", "Music Autotagging"),
        (
            "Superhuman mastery of arbitrary abstract strategy games",
            "Abstract Strategy Games",
        ),
        (
            "Play an arbitrary abstract game, first learning the rules",
            "Abstract Strategy Games with Rule Learning",
        ),
        (
            "Solve technical problems with clear constraints (proofs, circuit "
            "design, aerofoil design, etc)",
            "Constrained Problem Solving",
        ),
        (
            "Know how to prevent an autonomous AI agent from reproducing "
            "itself an unbounded number of times",
            "Restricted Reproduction",
        ),
        (
            "Transfer of learning within simple arcade game paradigms",
            "Arcade Game Transfer Learning",
        ),
        (
            "Train machine learning systems on private user data, without "
            "transferring sensitive facts into the model",
            "Privacy Preserving Machine Learning",
        ),
        ("Avoiding reward hacking", "Reward Hacking Avoidance"),
        ("Drawing pictures", "Image Generation"),
        ("Recognise events in videos", "Video Activity Recognition"),
        (
            "Correctly identify when an answer to a classification problem is "
            "uncertain",
            "Classification Under Uncertainty",
        ),
        (
            "Deploy automated defensive security tools to protect valuable "
            "systems",
            "Automated Security",
        ),
        (
            "Scalable supervision of a learning system",
            "Scalable Supervised Learning",
        ),
        ("Pedestrian, bicycle & obstacle detection", "Pedestrian Detection"),
        (
            "Given desired circuit characteristics, and many examples, design "
            "new circuits to spec",
            "Automated Circuit Design",
        ),
        (
            "One shot learning, ingest important truths from a single example",
            "One-Shot Learning",
        ),
        (
            "Language comprehension and question-answering",
            "Question Answering",
        ),
        (
            "Given examples of proofs, find correct proofs of simple "
            "mathematical theorems",
            "Mathematical Proofs",
        ),
        ("Games that require language comprehension", "Language Games"),
        (
            "Games that require both understanding and speaking a language",
            "Spoken Language Games",
        ),
        (
            "Learn a several tasks without undermining performance on a first "
            "task, avoiding catastrophic forgetting",
            "Catastrophic Forgetting Avoidance",
        ),
        (
            "Train ML classifiers in a manner that corrects for the impact of "
            "omitted-variable bias on certain groups",
            "Omitted-Variable Bias Correction",
        ),
        (
            "Given an arbitrary technical problem, solve it as well as a "
            "typical professional in that field",
            "Artificial General Intelligence",
        ),
        ("Writing software from specifications", "Code Generation"),
        ("Translation between human langauges", "Machine Translation"),
        (
            "Fairness in machine learning towards people with a preference "
            "for privacy",
            "Privacy Fairness",
        ),
        ("Safe exploration", "Safe Exploration"),
        (
            "Turing test for casual conversation",
            "Casual Conversation Turing Test",
        ),
        ("Write computer programs from specifications", "Code Generation"),
        (
            "Transfer learning, apply relevant knowledge from a prior setting "
            "to a new slightly different one",
            "Transfer Learning",
        ),
        ("Play real-time computer & video games", "Video Games"),
        (
            "Extract major numerical results or progress claims from a STEM "
            "paper",
            "Scientific Result Extraction",
        ),
        ("Abstract strategy games", "Abstract Strategy Games"),
        (
            "Cooperative inverse reinforcement learning of objective "
            "functions",
            "Objective Function Reinforcement Learning",
        ),
        (
            "Provide mathematical or technical explanations of decisions "
            "from classifiers",
            "Explainable Machine Learning",
        ),
        ("Image classification", "Image Classification"),
        (
            "Read a scientific or technical paper, and comprehend its "
            "contents",
            "Scientific Paper Comprehension",
        ),
        ("Answering Science Exam Questions", "Scientific Question Answering"),
        (
            "Conduct arbitrary sustained, probing conversation",
            "Automated Interrogation",
        ),
        (
            "Building systems that solve a wide range of diverse problems, "
            "rather than just specific ones",
            "Artificial General Intelligence",
        ),
        (
            "Modify arbitrary ML systems in order to be able to provide "
            "comprehensible human explanations of their decisions",
            "Explainable Machine Learning",
        ),
        (
            "Learning the rules of complex strategy games from examples",
            "Strategy Game Rule Learning",
        ),
        (
            "Know how to build general AI agents that will behave as expected",
            "Predictable Artificial General Intelligence",
        ),
        (
            "Build systems which can recognise and avoid biases decision "
            "making",
            "Bias Avoidance",
        ),
        (
            "Function correctly in novel environments (robustness to "
            "distributional change)",
            "Functional Robustness",
        ),
        (
            "Detect security-related bugs in codebases",
            "Security Bug Detection",
        ),
        ("Simple video games", "Simple Video Games"),
        (
            "Playing abstract games with extensive hints",
            "Abstract Games with Hints",
        ),
        ("Accurate modelling of human language.", "Language Modelling"),
        (
            "Games that require inventing novel language, forms of speech, or "
            "communication",
            "Language Creation Games",
        ),
        ("Resistance to adversarial examples", "Adversarial Defense"),
        (
            "Parse and implement complex conditional expressions",
            "Conditional Expression Parsing",
        ),
        ("Image comprehension", "Visual Question Answering"),
        (
            "Be able to generate complex scene e.g. a baboon receiving their "
            "degree at convocatoin.",
            "Complex Conditional Image Generation",
        ),
        (
            "Solve vaguely or under-constrained technical problems",
            "Underconstrained Problem Solving",
        ),
        ("Avoiding undesirable side effects", "Side Effect Mitigation"),
    ]
)
