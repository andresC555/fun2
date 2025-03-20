python_sources(
    name="api_gateway",
    sources=["src/**/*.py"],
    dependencies=[
        "//:shared",
    ],
)

python_tests(
    name="tests",
    sources=["tests/**/*.py"],
    dependencies=[
        ":api_gateway",
        "//:shared",
    ],
)

docker_image(
    name="docker",
    repository="monorepo/services/api_gateway",
    dependencies=[
        ":api_gateway",
    ],
    image_tags=["latest"],
)
