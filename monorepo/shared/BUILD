python_sources(
    name="shared",
    dependencies=[
        ":models",
        ":utils",
        ":db",
    ],
)

python_sources(
    name="models",
    sources=["models/**/*.py"],
)

python_sources(
    name="utils",
    sources=["utils/**/*.py"],
)

python_sources(
    name="db",
    sources=["db/**/*.py"],
    dependencies=[
        ":models",
    ],
)

python_tests(
    name="tests",
    sources=["tests/**/*.py"],
    dependencies=[
        ":shared",
    ],
)
