"""
utils.py: functions that will be used by the other modules
"""
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


def def_args_prefs(options, args, preferences):
    """
    def_args_prefs: generate the arguments and preferences for the ChromeDriver

    Args:
        options (chrome.options): _description_
        args (str[]|str): arguments for the chromedriver
        preferences (str[]): preferences for the chromedriver

    Returns:
        _type_: _description_
    """
    for arg in args:
        if isinstance(arg, list):
            options.add_argument(arg[0], arg[1])
        else:
            options.add_argument(arg)

    if preferences != []:
        options.add_experimental_option("prefs", preferences)

    return options


def click_fontawesome(driver, button_name="circle-xmark", exist=True):
    """
    click_fontawesome: click action in fontawesome frontend buttons

    Args:
        driver (webdriver.Chrome):webdriver Chrome that could represent the
    entire page or a part of the page
        button_name (str, optional): Button data-icon attribute. Defaults to
    "circle-xmark".
        exist (bool, optional): If set top true, it will perform a test and it
    will return a error if the button is not present. Defaults to True.
    """
    buttons = driver.find_elements(By.TAG_NAME, "svg")
    for button in buttons:
        if button.get_attribute("data-icon") == button_name:
            button.click()
            # it takes a few seconds for a popup to fully disappear
            sleep(3)
            return
    if exist:
        assert False


def clear_map(driver):
    """
    clear_map: click action in clear map button

    Args:
        driver (webdriver.Chrome):webdriver Chrome that could represent the
    entire page or a part of the page

    """
    trash = driver.find_element(By.XPATH, '//header[@title="Clean map"]')
    trash.click()


def check_info_section(driver, title, id_name="info-section-button", idx=0):
    """
    check_info_section: click to open and close info section

    Args:
        driver (webdriver.Chrome):webdriver Chrome that could represent the
    entire page or a part of the page

        title (str): title of the information box
        id_name (str, optional): id name of the button that will be clicked.
    Defaults to "info-section-button".
        idx (int, optional): if there is more than one button, it will click in
    the id of the button to open the correct info section. Defaults to 0.
    """
    info_section = driver.find_elements(By.ID, id_name)
    info_section = info_section[idx]
    info_section.click()
    result = driver.find_element(By.ID, "info-subsection")
    title_el = result.find_element(By.TAG_NAME, "p")
    assert title_el.text.lower() == title.lower()
    click_fontawesome(driver)
    result = driver.find_elements(By.ID, "info-subsection")
    assert len(result) == 0


def verify_map_plot(driver, result, option_selected):
    """
    verify_map_plot: verify if the graphs and circles on the survey design part
        are correctly generatade

    Args:
        driver (webdriver.Chrome): webdriver Chrome that could represent the
    entire page or a part of the page.
        result (webdriver.Chrome): webdriver Chrome that represents the
    component that has the plot area.
        option_selected (str): name of the options that was used to generate
    the graph
    """
    plot_container = result.find_element(By.CLASS_NAME, "plotly")
    lines = plot_container.find_elements(By.CLASS_NAME, "scatter")
    act_driver = ActionChains(driver)
    for line in lines:
        act_driver.move_to_element(line).perform()
    circles = driver.find_elements(By.CSS_SELECTOR, "svg.leaflet-zoom-animated>g path")
    assert circles[0].get_attribute("stroke") == "#ffd3c9"
    assert circles[1].get_attribute("stroke") == "#ff96bc"
    big_circle = circles[0].get_attribute("d")
    small_circle = circles[1].get_attribute("d")

    rangeslider_min = plot_container.find_element(
        By.CLASS_NAME, "rangeslider-grabber-min"
    )
    rangeslider_max = plot_container.find_element(
        By.CLASS_NAME, "rangeslider-grabber-max"
    )

    y_label_title = plot_container.find_element(By.CLASS_NAME, "ytitle")

    assert y_label_title.text == option_selected
    act_driver = ActionChains(driver)
    act_driver.click_and_hold(rangeslider_max).move_by_offset(
        -10, -10
    ).release().perform()
    circles = driver.find_elements(By.CSS_SELECTOR, "svg.leaflet-zoom-animated>g path")
    assert big_circle != circles[0].get_attribute("d")
    act_driver = ActionChains(driver)
    act_driver.click_and_hold(rangeslider_min).move_by_offset(
        10, 10
    ).release().perform()
    circles = driver.find_elements(By.CSS_SELECTOR, "svg.leaflet-zoom-animated>g path")
    new_small_circle = circles[1].get_attribute("d")
    new_big_circle = circles[0].get_attribute("d")
    assert small_circle != new_small_circle
    act_driver = ActionChains(driver)
    leaflet_map = driver.find_element(By.CLASS_NAME, "leaflet-container")
    act_driver = ActionChains(driver)
    act_driver.drag_and_drop_by_offset(leaflet_map, 100, 200).perform()
    sleep(2)
    circles = driver.find_elements(By.CSS_SELECTOR, "svg.leaflet-zoom-animated>g path")

    assert new_big_circle != circles[0].get_attribute("d")
    assert new_small_circle != circles[1].get_attribute("d")


def get_layers(driver, url_part="haig"):
    """
    get_layers: verify if a layer exist in the leaflet map

    Args:
        driver (webdriver.Chrome): webdriver Chrome that could represent the
    entire page or a part of the page.
        url_part (str, optional): url part that will be used to check which
    type of layer is the layer that it was found.

    Returns:
        new_layer: return a value that could be None or the selected layer
    """
    layers = driver.find_elements(By.CLASS_NAME, "leaflet-layer")
    new_layer = None
    for layer in layers:
        if len(layer.find_elements(By.TAG_NAME, "img")) > 0:
            src = layer.find_element(By.TAG_NAME, "img").get_attribute("src")
            if url_part in src:
                new_layer = layer
    return new_layer


def get_layers_mbtiles(driver):
    """
    get_layers_mbtiles: verify if a mbtiles layer exist in the leaflet map

    Args:
        driver (webdriver.Chrome): webdriver Chrome that could represent the
    entire page or a part of the page.

    Returns:
        new_layer: return a value that could be None or the selected layer
    """
    layers = driver.find_elements(By.CLASS_NAME, "leaflet-layer")
    new_layer = None
    for layer in layers:
        if layer.get_attribute("style")[-4:-2] == "0.":
            new_layer = layer
    return new_layer
