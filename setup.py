from setuptools import setup

setup(
    name="extra_qwidgets",
    version="0.0.1",
    author="gustavopedrosob",
    author_email="thevicio27@gmail.com",
    description="Extra widgets for Qt/PySide6",
    url="https://github.com/gustavopedrosob/ExtraQWidgets",
    project_urls={
        "Bug Tracker": "https://github.com/gustavopedrosob/ExtraQWidgets/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "source"},
    package_data={"": ["assets/emojis/*.png"]},
    include_package_data=True,
    packages=["extra_qwidgets",
              "extra_qwidgets.abc_widgets",
              "extra_qwidgets.abc_widgets.emoji_picker",
              "extra_qwidgets.widgets",
              "extra_qwidgets.widgets.emoji_picker",
              "extra_qwidgets.widgets.filterable_table",
              "extra_qwidgets.fluent_widgets",
              "extra_qwidgets.fluent_widgets.emoji_picker",
              "extra_qwidgets.proxys",
              "extra_qwidgets.validators"],
    install_requires=["emojis", "PySide6", "emoji"],
    python_requires=">=3.12"
)
