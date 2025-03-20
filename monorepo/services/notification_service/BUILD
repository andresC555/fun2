python_sources(
    name="notification_service",
    sources=["src/**/*.py"],
    dependencies=[
        "//:shared",
    ],
)

python_tests(
    name="tests",
    sources=["tests/**/*.py"],
    dependencies=[
        ":notification_service",
        "//:shared",
    ],
)

docker_image(
    name="docker",
    repository="monorepo/services/notification_service",
    dependencies=[
        ":notification_service",
    ],
    image_tags=["latest"],
)
