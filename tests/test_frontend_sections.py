from contextlib import contextmanager
from time import sleep

import pytest
from playwright.sync_api import Page, TimeoutError, expect

LOCAL_TEST = False

PORT = "8503" if LOCAL_TEST else "8699"


@contextmanager
def run_streamlit():
    """Run the streamlit app at example_app/streamlit_app_sections.py on port 8599"""
    import subprocess

    if LOCAL_TEST:
        try:
            yield 1
        finally:
            pass
    else:
        p = subprocess.Popen(
            [
                "streamlit",
                "run",
                "example_app/streamlit_app_sections.py",
                "--server.port",
                PORT,
                "--server.headless",
                "true",
            ]
        )

        sleep(5)

        try:
            yield 1
        finally:
            p.kill()


@pytest.fixture(scope="module", autouse=True)
def before_module():
    # Run the streamlit app before each module
    with run_streamlit():
        yield


@pytest.fixture(scope="function", autouse=True)
def before_test(page: Page):
    page.goto(f"localhost:{PORT}")


def test_pages_clickable(page: Page):
    try:
        expect(page.get_by_text("🏠 Home")).to_be_visible()
    except Exception:
        page.screenshot(path="screenshot_sections1-full.png", full_page=True)
        raise

    page.get_by_role("link", name="Example One").click()

    expect(page).to_have_title("Example One")


def test_sections_unclickable(page: Page):
    expect(page.get_by_text("🏠 Home")).to_be_visible()
    page.screenshot(path="screenshot_sections.png")

    # Check that section title is visible
    expect(page.get_by_role("link", name="Cool apps")).to_be_visible()

    # Check that section title is not clickable
    with pytest.raises(TimeoutError):
        page.get_by_role("link", name="Cool apps").click(timeout=5)


def test_deprecation_warning(page: Page):
    expect(
        page.get_by_text("st.experimental_singleton is deprecated")
    ).not_to_be_visible()


def test_in_section_false(page: Page):
    bbox_not_in_section = (
        page.get_by_role("link", name="Example Five")
        .get_by_text("Example Five")
        .bounding_box()
    )
    bbox_in_section = (
        page.get_by_role("link", name="Example Four")
        .get_by_text("Example Four")
        .bounding_box()
    )

    assert bbox_in_section is not None
    assert bbox_not_in_section is not None

    # Check that the in_section=False page is at least 10 pixels to the left of the
    # in_section=True page
    assert bbox_not_in_section["x"] < bbox_in_section["x"] - 10
