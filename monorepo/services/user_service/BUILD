python_sources(
    name="user_service",
    sources=["src/**/*.py"],
    dependencies=[
        "//:shared",
    ],
)

python_tests(
    name="tests",
    sources=["tests/**/*.py"],
    dependencies=[
        ":user_service",
        "//:shared",
    ],
)

docker_image(
    name="docker",
    repository="monorepo/services/user_service",
    dependencies=[
        ":user_service",
    ],
    image_tags=["latest"],
)
