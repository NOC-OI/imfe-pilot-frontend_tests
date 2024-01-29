"""
Pytest codes for the Frontend Haig Fras.
It is based on pytest and selenium.
To run the tests, you need to run make test
"""
from time import sleep
import os
import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

import requests
from frontend_test.utils import (
    def_args_prefs,
    clear_map,
    click_fontawesome,
    get_layers_mbtiles,
    get_layers,
    verify_map_plot,
    check_info_section,
)


@pytest.fixture(scope="class")
def driver_init(request):
    """
    driver_init: initialization of the driver using a fixture that
        shares requested elements with scope class (other classes).
        In this case, the following elements are being sharing: driver and url.

    Args:
        request: The request fixture is a special fixture providing information
    of the requesting test function
    """
    mode = os.getenv("SELENIUM_MODE")
    args = []
    if mode == "HEADLESS":
        args.append("--headless")

    preferences = []

    if os.getenv("SELENIUM_BROWSER") == "firefox":
        from selenium.webdriver.firefox.options import Options
        options = def_args_prefs(Options(), args, preferences)
        driver = webdriver.Firefox(options=options)
    else:
        from selenium.webdriver.chrome.options import Options
        args += ["--no-sandbox", "--disable-dev-shm-usage"]
        options = def_args_prefs(Options(), args, preferences)
        driver = webdriver.Chrome(options=options)

    driver.set_window_size(1920, 1080)
    driver.maximize_window()

    request.cls.driver = driver
    request.cls.url = os.getenv("FRONTEND_URL_LOCAL")
    yield
    driver.close()


@pytest.mark.usefixtures("driver_init")
class Test_URL:
    """
    Test_URL: class to perform the tests. It uses the fixtures from driver_init
            test_open_url: test for open the url
    """

    load_dotenv()

    def test_open_url(self):
        """
        test_open_url: test for open the url
        """
        self.driver.get(self.url)
        assert self.driver.title == "Haig Fras - Digital Twin"

    def test_data_exploration_bathymetry_graph_remove(self):
        """
        test_data_exploration_bathymetry_graph_remove: test for verify if graph
            is remove when graph icon is clicked
        """

        driver = self.driver
        driver.get(self.url)
        # clear the initial welcome screen
        wait = WebDriverWait(driver, 30)
        wait.until(EC.invisibility_of_element_located((By.ID, "loading")))
        click_fontawesome(driver)

        section_name = "Data Exploration"
        button = driver.find_element(By.ID, section_name)
        button.click()

        buttons = driver.find_elements(By.XPATH, "//span[@title='expand']")

        buttons[0].click()
        type_options = driver.find_elements(By.ID, "type-option")
        type_option = type_options[0]
        check_layer = type_option.find_element(By.TAG_NAME, "input")
        check_layer.click()
        sleep(6)
        layer_edit = driver.find_elements(By.ID, "layer-edit")
        assert len(layer_edit) > 0
        click_fontawesome(driver=layer_edit[0], button_name="chart-simple")
        flash_message = driver.find_elements(By.ID, "flash-message")
        assert len(flash_message) > 0
        leaflet_map = driver.find_element(By.CLASS_NAME, "leaflet-container")
        act_driver = ActionChains(driver)
        act_driver.move_to_element(leaflet_map)
        act_driver.perform()
        act_driver.move_by_offset(50, 50)
        act_driver.perform()
        act_driver.click()
        act_driver.perform()
        act_driver.move_to_element(leaflet_map)
        act_driver.perform()
        act_driver.move_by_offset(100, 100)
        act_driver.perform()
        act_driver.click()
        act_driver.perform()
        graph_box = driver.find_elements(By.ID, "graph-box")
        assert len(graph_box) > 0

        wait = WebDriverWait(driver, 7)
        graph = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "plotly")))
        assert graph

        click_fontawesome(driver=layer_edit[0], button_name="chart-simple")
        graph_box = driver.find_elements(By.ID, "graph-box")
        assert len(graph_box) == 0

        act_driver = ActionChains(driver)
        act_driver.move_to_element(leaflet_map)
        act_driver.perform()
        act_driver.move_by_offset(50, 50)
        act_driver.perform()
        act_driver.click()
        act_driver.perform()
        act_driver.move_to_element(leaflet_map)
        act_driver.perform()
        act_driver.move_by_offset(100, 100)
        act_driver.perform()

        click_fontawesome(driver=layer_edit[0], button_name="chart-simple")
        graph_box = driver.find_elements(By.ID, "graph-box")
        assert len(graph_box) == 0

        self.driver = driver

    def test_biodiversity_polygon(self):
        """
        test_biodiversity_polygon: test if limits is being plotted in the map
            on click.
        """
        driver = self.driver
        driver.get(self.url)
        wait = WebDriverWait(driver, 30)
        wait.until(EC.invisibility_of_element_located((By.ID, "loading")))
        click_fontawesome(driver)
        section_name = "Biodiversity"
        button = driver.find_element(By.ID, section_name)
        button.click()
        sleep(5)
        buttons = driver.find_elements(By.ID, "general-types")
        assert len(buttons) > 0
        for button in buttons:
            if button.text != 'Interannual Monitoring':
                button.click()
                type_options = driver.find_elements(By.ID, "type-option")
                for type_option in type_options:
                    polygons = driver.find_elements(
                        By.CSS_SELECTOR, "svg.leaflet-zoom-animated>g path"
                    )
                    assert len(polygons) == 0
                    type_option.click()
                    wait = WebDriverWait(driver, 10)
                    wait.until(EC.visibility_of_element_located((By.ID, "calculate-value")))
                    polygons = driver.find_elements(
                        By.CSS_SELECTOR, "svg.leaflet-zoom-animated>g path"
                    )
                    assert len(polygons) > 0

                    clear_map(driver)

        self.driver = driver

    def test_close_open_popup(self):
        """
        test_close_open_popup: test for open and close the first popup
        """

        driver = self.driver
        self.driver.get(self.url)
        title = self.driver.find_element(By.TAG_NAME, "h2")
        assert title.text == "Haig Fras Digital Twin - Pilot Study"

        click_fontawesome(driver)
        elements = self.driver.find_elements(By.TAG_NAME, "h2")
        assert len(elements) == 0
        click_fontawesome(driver, button_name="circle-question")
        elements = self.driver.find_elements(By.TAG_NAME, "h2")
        assert len(elements) > 0
        click_fontawesome(driver)
        elements = self.driver.find_elements(By.TAG_NAME, "h2")
        assert len(elements) == 0

        self.driver = driver

    def test_habitats(self):
        """
        test_habitats: test for verify habitats tab from the side bar
        """
        driver = self.driver
        driver.get(self.url)
        wait = WebDriverWait(driver, 30)
        wait.until(EC.invisibility_of_element_located((By.ID, "loading")))
        click_fontawesome(driver)
        section_name = "Seabed Types"
        button = driver.find_element(By.ID, section_name)
        button.click()

        section_title = driver.find_elements(By.TAG_NAME, "h1")
        assert section_title[0].text == section_name

        check_info_section(driver, section_name)

        buttons = driver.find_elements(By.XPATH, "//span[@title='expand']")
        assert len(buttons) == 2

        for button in buttons:
            button.click()
            sub_items = driver.find_elements(By.ID, "type-option")
            for sub_item in sub_items:
                sub_item.click()
                wait = WebDriverWait(driver, 10)
                result = wait.until(
                    EC.visibility_of_element_located((By.ID, "calculate-value"))
                )
                if sub_item.text[0:6] == 'Number':
                    assert len(result.text) > 5
                if sub_item.text[0:4] == 'Type':
                    wait = WebDriverWait(driver, 10)
                    result = wait.until(
                        EC.visibility_of_element_located((By.ID, "calculate-value"))
                    )
                    card_types = result.find_elements(By.TAG_NAME, "button")
                    assert len(card_types) > 2
                    for card_type in card_types:
                        image = card_type.find_element(By.CSS_SELECTOR, "img")
                        response = requests.get(image.get_attribute("src"), timeout=5)
                        assert response.status_code == 200
                    card_types[0].click()
                    map_icons = driver.find_elements(By.CLASS_NAME, "all-icon")
                    assert len(map_icons) > 10
                    map_limit = driver.find_elements(
                        By.CSS_SELECTOR, "svg.leaflet-zoom-animated>g path"
                    )
                    assert len(map_limit) > 0
                    assert map_limit[0].get_attribute("fill-opacity") == "0.7"
                    clear_map(driver)
                    map_icons = driver.find_elements(By.CLASS_NAME, "all-icon")
                    assert len(map_icons) == 0
                click_fontawesome(driver)

            button.click()

        button = driver.find_element(By.ID, section_name)
        button.click()

        section_title = driver.find_elements(By.TAG_NAME, "h1")
        assert len(section_title) == 1

        self.driver = driver

    def test_species(self):
        """
        test_species: test for verify indicator species
        """
        driver = self.driver
        driver.get(self.url)
        wait = WebDriverWait(driver, 30)
        wait.until(EC.invisibility_of_element_located((By.ID, "loading")))
        click_fontawesome(driver)
        section_name = "Species of Interest"
        button = driver.find_element(By.ID, section_name)
        button.click()
        sleep(10)

        section_title = driver.find_elements(By.TAG_NAME, "h1")
        assert section_title[0].text == section_name

        check_info_section(driver, section_name)

        buttons = driver.find_elements(By.XPATH, "//span[@title='expand']")
        assert len(buttons) > 1

        buttons[0].click()

        organisms = ["Pentapora foliacea", "Cartilagenous fish"]
        for organism in organisms:
            sleep(10)
            name = driver.find_elements(By.XPATH, f"//em[text()='{organism}']")
            print(name)
            if len(name) == 0:
                name = driver.find_elements(By.XPATH, f"//p[text()='{organism}']")
            name[0].click()
            wait = WebDriverWait(driver, 10)
            result = wait.until(
                EC.visibility_of_element_located((By.ID, "calculate-value"))
            )
            assert len(result.text) > 5
            paragraph = result.find_elements(By.TAG_NAME, "p")
            assert paragraph[0].text == organism
            card_types = result.find_elements(By.TAG_NAME, "button")
            assert len(card_types) > 0
            for card_type in card_types:
                image = card_type.find_element(By.CSS_SELECTOR, "img")
                response = requests.get(image.get_attribute("src"), timeout=5)
                assert response.status_code == 200
            map_icons = driver.find_elements(By.CLASS_NAME, "all-icon")
            assert len(map_icons) > 0
            map_limit = driver.find_elements(
                By.CSS_SELECTOR, "svg.leaflet-zoom-animated>g path"
            )
            assert len(map_limit) > 0
            assert map_limit[0].get_attribute("fill-opacity") == "0.7"
            click_fontawesome(driver)
            clear_map(driver)
            map_icons = driver.find_elements(By.CLASS_NAME, "all-icon")
            assert len(map_icons) == 0
        button = driver.find_element(By.ID, section_name)
        button.click()

        section_title = driver.find_elements(By.TAG_NAME, "h1")
        assert len(section_title) == 1

        self.driver = driver

    def test_biodiversity(self):
        """
        test_biodiversity: test for verify biodiversity tab
        """
        driver = self.driver
        driver.get(self.url)
        wait = WebDriverWait(driver, 30)
        wait.until(EC.invisibility_of_element_located((By.ID, "loading")))
        click_fontawesome(driver)
        section_name = "Biodiversity"
        button = driver.find_element(By.ID, section_name)
        button.click()

        section_title = driver.find_elements(By.TAG_NAME, "h1")
        assert section_title[0].text == section_name

        check_info_section(driver, section_name)

        general_types = driver.find_elements(By.ID, "general-types")
        for idx, general_type in enumerate(general_types):
            check_info_section(
                driver,
                title=general_type.text,
                id_name="info-subsection-button",
                idx=idx,
            )

        buttons = driver.find_elements(By.ID, "general-types")
        assert len(buttons) > 0
        for button in buttons:
            if button.text != 'Interannual Monitoring':
                button.click()
                type_options = driver.find_elements(By.ID, "type-option")
                for type_option in type_options:
                    type_options_text = type_option.text
                    type_option.click()
                    wait = WebDriverWait(driver, 10)
                    result = wait.until(
                        EC.visibility_of_element_located((By.ID, "calculate-value"))
                    )
                    assert len(result.text) > 5
                    paragraph = result.find_elements(By.TAG_NAME, "p")
                    assert paragraph[0].text == type_options_text
                    if type_options_text != "Morphotypes":
                        card_types = result.find_elements(By.TAG_NAME, "button")
                        assert len(card_types) > 0
                        click_fontawesome(driver)

        button = driver.find_element(By.ID, section_name)
        button.click()

        section_title = driver.find_elements(By.TAG_NAME, "h1")
        assert len(section_title) == 1

        self.driver = driver

    def test_survey_design(self):
        """
        test_survey_design: test for verify survey design tab
        """
        driver = self.driver
        driver.get(self.url)
        wait = WebDriverWait(driver, 30)
        wait.until(EC.invisibility_of_element_located((By.ID, "loading")))
        click_fontawesome(driver)

        section_name = "Survey Design"
        button = driver.find_element(By.ID, section_name)
        button.click()

        section_title = driver.find_elements(By.TAG_NAME, "h1")
        assert section_title[0].text == section_name

        check_info_section(driver, section_name)

        # general_types = driver.find_elements(By.ID, "general-types")
        # for idx, general_type in enumerate(general_types):
        #     check_info_section(
        #         driver,
        #         title=general_type.text,
        #         id_name="info-subsection-button",
        #         idx=idx,
        #     )

        buttons = driver.find_elements(By.XPATH, "//span[@title='expand']")
        assert len(buttons) > 0

        buttons[0].click()
        type_options = driver.find_elements(By.ID, "type-option")
        for type_option in type_options:
            type_options_text = type_option.text
            type_option.click()
            wait = WebDriverWait(driver, 10)
            result = wait.until(
                EC.visibility_of_element_located((By.ID, "dynamic-graph"))
            )
            select_box = Select(driver.find_element(By.ID, "select_habitat"))
            number_options = len(select_box.options)
            for option_idx in range(number_options):
                if option_idx > 0:
                    select_box = Select(driver.find_element(By.ID, "select_habitat"))
                    select_box.select_by_index(option_idx)
                    wait = WebDriverWait(driver, 10)
                    result = wait.until(
                        EC.visibility_of_element_located((By.ID, "dynamic-graph"))
                    )
                assert len(result.text) > 5
                paragraph = result.find_elements(By.TAG_NAME, "p")
                assert paragraph[0].text == type_options_text
                hover_values = result.find_elements(By.ID, "hover-value")
                assert len(hover_values) == 0
                range_values = result.find_elements(By.ID, "range-value")
                assert len(range_values) == 2
                select_box_bios = driver.find_elements(By.ID, "select_biodiversity")
                if len(select_box_bios) > 0:
                    select_box_bio = Select(
                        driver.find_element(By.ID, "select_biodiversity")
                    )
                    number_options_bio = len(select_box_bio.options)
                    for option_bio_idx in range(number_options_bio):
                        select_box_bio = Select(
                            driver.find_element(By.ID, "select_biodiversity")
                        )
                        option_selected_bio = select_box_bio.options[
                            number_options_bio - option_bio_idx - 1
                        ].text
                        select_box_bio.select_by_index(
                            number_options_bio - option_bio_idx - 1
                        )
                        sleep(5)
                        verify_map_plot(driver, result, option_selected_bio)
                else:
                    verify_map_plot(driver, result, "Density (counts/m2)")

        button = driver.find_element(By.ID, section_name)
        button.click()

        section_title = driver.find_elements(By.TAG_NAME, "h1")
        assert len(section_title) == 1

        self.driver = driver

    def test_data_exploration_bathymetry(self):
        """
        test_data_exploration_bathymetry: test for verify data exploration
            bathymetry
        """

        driver = self.driver
        driver.get(self.url)
        wait = WebDriverWait(driver, 30)
        wait.until(EC.invisibility_of_element_located((By.ID, "loading")))
        click_fontawesome(driver)

        section_name = "Data Exploration"
        button = driver.find_element(By.ID, section_name)
        button.click()

        section_title = driver.find_elements(By.TAG_NAME, "h1")
        assert section_title[0].text == section_name

        check_info_section(driver, section_name)

        buttons = driver.find_elements(By.XPATH, "//span[@title='expand']")
        assert len(buttons) > 0

        buttons[0].click()
        type_options = driver.find_elements(By.ID, "type-option")
        type_option = type_options[0]
        layer_edit = driver.find_elements(By.ID, "layer-edit")
        assert len(layer_edit) == 0
        new_layer = get_layers(driver)
        assert not new_layer
        check_layer = type_option.find_element(By.TAG_NAME, "input")
        check_layer.click()
        sleep(30)
        layer_edit = driver.find_elements(By.ID, "layer-edit")
        assert len(layer_edit) > 0
        new_layer = get_layers(driver)
        assert new_layer
        general_types = driver.find_elements(By.ID, "general-types")
        check_info_section(
            driver,
            title=f"{general_types[0].text} - {type_option.text}",
            id_name="info-subsection-button",
        )

        layer_values = (
            new_layer.get_attribute("style")
            .replace(":", "")
            .replace(";", "")
            .split(" ")
        )
        click_fontawesome(driver=layer_edit[0], button_name="magnifying-glass")
        new_layer = get_layers(driver)
        layer_values_new = (
            new_layer.get_attribute("style")
            .replace(":", "")
            .replace(";", "")
            .split(" ")
        )
        assert int(layer_values[1]) < int(layer_values_new[1])
        input_range = driver.find_elements(By.XPATH, "//input[@type='range']")
        assert len(input_range) == 0
        click_fontawesome(driver=layer_edit[0], button_name="sliders")
        input_range = driver.find_elements(By.XPATH, "//input[@type='range']")
        assert len(input_range) > 0
        input_range[0].send_keys(Keys.LEFT)
        new_layer = get_layers(driver)
        layer_values_new = (
            new_layer.get_attribute("style")
            .replace(":", "")
            .replace(";", "")
            .split(" ")
        )
        assert float(layer_values[3]) > float(layer_values_new[3])
        flash_message = driver.find_elements(By.ID, "flash-message")
        assert len(flash_message) == 0
        click_fontawesome(driver=layer_edit[0], button_name="chart-simple")
        flash_message = driver.find_elements(By.ID, "flash-message")
        assert len(flash_message) > 0

        leaflet_map = driver.find_element(By.CLASS_NAME, "leaflet-container")
        act_driver = ActionChains(driver)
        act_driver.move_to_element(leaflet_map)
        act_driver.perform()
        act_driver.move_by_offset(50, 50)
        act_driver.perform()
        act_driver.click()
        act_driver.perform()
        act_driver.move_to_element(leaflet_map)
        act_driver.perform()
        act_driver.move_by_offset(100, 100)
        act_driver.perform()
        act_driver.click()
        act_driver.perform()
        graph_box = driver.find_elements(By.ID, "graph-box")
        assert len(graph_box) > 0

        wait = WebDriverWait(driver, 7)
        graph = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "plotly")))
        lines = graph.find_elements(By.CLASS_NAME, "scatter")
        assert len(lines) > 0
        x_label = graph.find_element(By.CLASS_NAME, "xtitle")
        assert x_label.text == "Distance (km)"
        click_fontawesome(driver)
        graph_box = driver.find_elements(By.ID, "graph-box")
        assert len(graph_box) == 0
        check_layer.click()
        new_layer = get_layers(driver)
        assert not new_layer

        button = driver.find_element(By.ID, section_name)
        button.click()

        section_title = driver.find_elements(By.TAG_NAME, "h1")
        assert len(section_title) == 1

        self.driver = driver

    def test_data_exploration_images(self):
        """
        test_data_exploration_images: test for verify data exploration for
            images
        """
        driver = self.driver
        driver.get(self.url)
        wait = WebDriverWait(driver, 30)
        wait.until(EC.invisibility_of_element_located((By.ID, "loading")))
        click_fontawesome(driver)

        section_name = "Data Exploration"
        button = driver.find_element(By.ID, section_name)
        button.click()

        section_title = driver.find_elements(By.TAG_NAME, "h1")
        assert section_title[0].text == section_name

        check_info_section(driver, section_name)

        buttons = driver.find_elements(By.ID, "general-types")
        assert len(buttons) > 0
        for button in buttons:
            if button.text == 'Seabed Images':
                general_type = button
                button.click()
        type_options = driver.find_elements(By.ID, "type-option")
        type_option = type_options[0]
        layer_edit = driver.find_elements(By.ID, "layer-edit")
        assert len(layer_edit) == 0
        polygons = driver.find_elements(
            By.CSS_SELECTOR, "svg.leaflet-zoom-animated>g path"
        )
        assert len(polygons) == 0
        map_icons = driver.find_elements(By.CLASS_NAME, "all-icon")
        assert len(map_icons) == 0
        check_layer = type_option.find_element(By.TAG_NAME, "input")
        #check test in this part
        sleep(3)
        check_layer.click()
        sleep(3)
        check_layer.click()
        sleep(3)
        check_layer.click()
        wait = WebDriverWait(driver, 5)
        map_icon = wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "all-icon"))
        )
        assert map_icon
        polygons = driver.find_elements(
            By.CSS_SELECTOR, "svg.leaflet-zoom-animated>g path"
        )
        assert len(polygons) > 0
        opacity = polygons[0].get_attribute("fill-opacity")
        map_icons = driver.find_elements(By.CLASS_NAME, "all-icon")
        assert len(map_icons) > 0
        layer_edit = driver.find_elements(By.ID, "layer-edit")
        assert len(layer_edit) > 0
        click_fontawesome(driver=layer_edit[0], button_name="sliders")
        input_range = driver.find_elements(By.XPATH, "//input[@type='range']")
        assert len(input_range) > 0
        input_range[0].send_keys(Keys.LEFT)
        polygons = driver.find_elements(
            By.CSS_SELECTOR, "svg.leaflet-zoom-animated>g path"
        )
        new_opacity = polygons[0].get_attribute("fill-opacity")
        assert float(opacity) > float(new_opacity)
        check_info_section(
            driver,
            title=f"{general_type.text} - {type_option.text}",
            id_name="info-subsection-button",
        )

        click_fontawesome(driver=layer_edit[0], button_name="sliders")
        input_range = driver.find_elements(By.XPATH, "//input[@type='range']")
        assert len(input_range) == 0

        map_icon = driver.find_element(By.CLASS_NAME, "leaflet-marker-icon")
        act_driver = ActionChains(driver)
        act_driver.move_to_element(map_icon)
        act_driver.perform()
        act_driver.click(map_icon)
        act_driver.perform()

        wait = WebDriverWait(driver, 7)
        map_icon_red = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//img[@src='/marker-icon_red.png']")
            )
        )
        assert map_icon_red
        sleep(5)
        popup = driver.find_element(By.CLASS_NAME, "leaflet-popup-content")
        sleep(5)
        assert type_option.text.lower() in popup.text.lower()
        check_layer.click()
        polygons = driver.find_elements(
            By.CSS_SELECTOR, "svg.leaflet-zoom-animated>g path"
        )
        assert len(polygons) == 0
        map_icons = driver.find_elements(By.CLASS_NAME, "all-icon")
        assert len(map_icons) == 0
        buttons = driver.find_elements(By.ID, "general-types")
        for button in buttons:
            if button.text == 'Seabed Images':
                button.click()

        button = driver.find_element(By.ID, section_name)
        button.click()

        section_title = driver.find_elements(By.TAG_NAME, "h1")
        assert len(section_title) == 1

        self.driver = driver

    def test_data_mbtiles(self):
        """
        test_data_mbtiles: test for verify mbtiles layers
        """

        driver = self.driver
        driver.get(self.url)
        wait = WebDriverWait(driver, 30)
        wait.until(EC.invisibility_of_element_located((By.ID, "loading")))
        click_fontawesome(driver)

        section_name = "Data Exploration"
        button = driver.find_element(By.ID, section_name)
        button.click()

        section_title = driver.find_elements(By.TAG_NAME, "h1")
        assert section_title[0].text == section_name

        check_info_section(driver, section_name)

        buttons = driver.find_elements(By.ID, "general-types")
        assert len(buttons) > 0
        for button in buttons:
            if button.text == 'Seabed Habitats':
                general_type = button
                button.click()
        type_options = driver.find_elements(By.ID, "type-option")
        for option in type_options:
            if option.text.lower() == 'seabed habitats-mbtiles':
                type_option = option
        layer_edit = driver.find_elements(By.ID, "layer-edit")
        assert len(layer_edit) == 0
        new_layer = get_layers_mbtiles(driver)
        assert not new_layer

        check_layer = type_option.find_element(By.TAG_NAME, "input")
        check_layer.click()
        sleep(5)
        driver.find_element(By.CLASS_NAME, "leaflet-control-zoom-out").click()
        sleep(5)
        new_layer = get_layers_mbtiles(driver)
        assert new_layer
        layer_values = (
            new_layer.get_attribute("style")
            .replace(":", "")
            .replace(";", "")
            .split(" ")
        )
        layer_edit = driver.find_elements(By.ID, "layer-edit")
        assert len(layer_edit) > 0
        input_range = driver.find_elements(By.XPATH, "//input[@type='range']")
        assert len(input_range) == 0
        click_fontawesome(driver=layer_edit[0], button_name="sliders")
        input_range = driver.find_elements(By.XPATH, "//input[@type='range']")
        assert len(input_range) > 0
        input_range[0].send_keys(Keys.LEFT)
        new_layer = get_layers_mbtiles(driver)
        layer_values_new = (
            new_layer.get_attribute("style")
            .replace(":", "")
            .replace(";", "")
            .split(" ")
        )
        assert float(layer_values[3]) > float(layer_values_new[3])

        click_fontawesome(driver=layer_edit[0], button_name="list")
        sleep(3)
        legend_box = driver.find_elements(By.ID, "legend-box")
        assert len(legend_box) > 0
        assert type_option.text in legend_box[0].text

        legend_items = legend_box[0].find_elements(By.TAG_NAME, "p")
        assert len(legend_items) > 0
        assert legend_items[0].text == "A5.37: Deep circalittoral mud"
        click_fontawesome(driver)
        legend_box = driver.find_elements(By.ID, "legend-box")
        assert len(legend_box) == 0

        leaflet_map = driver.find_element(By.CLASS_NAME, "leaflet-container")
        act_driver = ActionChains(driver)
        act_driver.move_to_element(leaflet_map)
        act_driver.perform()
        act_driver.move_by_offset(50, 50)
        act_driver.perform()
        act_driver.click()
        act_driver.perform()

        wait = WebDriverWait(driver, 10)
        popup = wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "leaflet-popup-content"))
        )
        assert "Energy" in popup.text

        check_info_section(
            driver,
            title=f"{general_type.text} - {type_option.text}",
            id_name="info-subsection-button",
        )

        buttons = driver.find_elements(By.XPATH, "//span[@title='expand']")
        buttons[4].click()

        button = driver.find_element(By.ID, section_name)
        button.click()

        section_title = driver.find_elements(By.TAG_NAME, "h1")
        assert len(section_title) == 1

        self.driver = driver

    def test_data_wms(self):
        """
        test_data_wms: test for verify wms layers
        """
        driver = self.driver
        driver.get(self.url)
        wait = WebDriverWait(driver, 30)
        wait.until(EC.invisibility_of_element_located((By.ID, "loading")))
        click_fontawesome(driver)

        section_name = "Data Exploration"
        button = driver.find_element(By.ID, section_name)
        button.click()

        section_title = driver.find_elements(By.TAG_NAME, "h1")
        assert section_title[0].text == section_name

        check_info_section(driver, section_name)

        buttons = driver.find_elements(By.ID, "general-types")
        assert len(buttons) > 0
        for button in buttons:
            if button.text == 'Seabed Habitats':
                general_type = button
                button.click()

        type_options = driver.find_elements(By.ID, "type-option")
        type_option = type_options[0]
        layer_edit = driver.find_elements(By.ID, "layer-edit")
        assert len(layer_edit) == 0
        new_layer = get_layers_mbtiles(driver)
        assert not new_layer

        check_layer = type_option.find_element(By.TAG_NAME, "input")
        check_layer.click()
        sleep(7)
        new_layer = get_layers(driver, url_part="seabedhabitats")
        assert new_layer
        layer_values = (
            new_layer.get_attribute("style")
            .replace(":", "")
            .replace(";", "")
            .split(" ")
        )
        layer_edit = driver.find_elements(By.ID, "layer-edit")
        assert len(layer_edit) > 0
        input_range = driver.find_elements(By.XPATH, "//input[@type='range']")
        assert len(input_range) == 0
        click_fontawesome(driver=layer_edit[0], button_name="sliders")
        input_range = driver.find_elements(By.XPATH, "//input[@type='range']")
        assert len(input_range) > 0
        input_range[0].send_keys(Keys.LEFT)
        new_layer = get_layers(driver, url_part="seabedhabitats")
        layer_values_new = (
            new_layer.get_attribute("style")
            .replace(":", "")
            .replace(";", "")
            .split(" ")
        )
        assert float(layer_values[3]) > float(layer_values_new[3])

        click_fontawesome(driver=layer_edit[0], button_name="list")
        sleep(3)
        legend_box = driver.find_elements(By.ID, "legend-box")
        assert len(legend_box) > 0
        assert type_option.text in legend_box[0].text
        legend_image = legend_box[0].find_elements(By.TAG_NAME, "img")
        assert len(legend_image) > 0
        click_fontawesome(driver)
        legend_box = driver.find_elements(By.ID, "legend-box")
        assert len(legend_box) == 0

        leaflet_map = driver.find_element(By.CLASS_NAME, "leaflet-container")
        act_driver = ActionChains(driver)
        act_driver.move_to_element(leaflet_map)
        act_driver.perform()
        act_driver.move_by_offset(50, 50)
        act_driver.perform()
        act_driver.click()
        act_driver.perform()
        wait = WebDriverWait(driver, 10)
        popup = wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "leaflet-popup-content"))
        )
        assert popup

        check_info_section(
            driver,
            title=f"{general_type.text} - {type_option.text}",
            id_name="info-subsection-button",
        )

        buttons = driver.find_elements(By.ID, "general-types")
        assert len(buttons) > 0
        for button in buttons:
            if button.text == 'Seabed Habitats':
                button.click()

        button = driver.find_element(By.ID, section_name)
        button.click()

        section_title = driver.find_elements(By.TAG_NAME, "h1")
        assert len(section_title) == 1

        self.driver = driver

    def test_infobox(self):
        """
        test_infobox: test for verify infobox layer
        """
        driver = self.driver
        driver.get(self.url)
        wait = WebDriverWait(driver, 30)
        wait.until(EC.invisibility_of_element_located((By.ID, "loading")))
        click_fontawesome(driver)
        sleep(2)
        infobox_container = driver.find_element(By.ID, "infobox-container")
        assert "---" in infobox_container.text
        leaflet_map = driver.find_element(By.CLASS_NAME, "leaflet-container")
        act_driver = ActionChains(driver)
        act_driver.move_to_element(leaflet_map)
        act_driver.perform()
        act_driver.move_by_offset(50, 50)
        act_driver.perform()
        act_driver.click()
        act_driver.perform()
        infobox_container = driver.find_element(By.ID, "infobox-container")
        assert "---" not in infobox_container.text

        self.driver = driver
