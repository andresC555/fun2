python_sources(
    name="product_service",
    sources=["src/**/*.py"],
    dependencies=[
        "//:shared",
    ],
)

python_tests(
    name="tests",
    sources=["tests/**/*.py"],
    dependencies=[
        ":product_service",
        "//:shared",
    ],
)

docker_image(
    name="docker",
    repository="monorepo/services/product_service",
    dependencies=[
        ":product_service",
    ],
    image_tags=["latest"],
)
