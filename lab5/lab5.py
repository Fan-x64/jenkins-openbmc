import pytest
import requests
import logging
import time
import json
import subprocess
from requests.exceptions import RequestException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

URL= "127.0.0.1:2443"

@pytest.fixture(scope="module")
#===============Авторизация в BMC=================
def autentification_Bmc():
    url = f"https://{URL}/redfish/v1/SessionService/Sessions"
    payload = {
        "UserName": "root",
        "Password": "0penBmc"
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, verify=False)
        response.raise_for_status()
        session_token = response.headers.get("X-Auth-Token")
        if not session_token:
            raise ValueError("Токен аутентификации не найден в заголовках ответа")
        logger.info("Вход в BMC выполнен успешно")
        yield session_token
    except RequestException as e:
        logger.error(f"Вход провален: {e}")
        pytest.fail("Ошибка аутентификации BMC")


#================Тесты=================
def test_autentification_Bmc(autentification_Bmc):
    url = f"https://{URL}/redfish/v1/SessionService/Sessions"
    playload = {
        "UserName": "root",
        "Password": "0penBmc"
    }
    headers = {
        "Content-Type": "application/json",
    }
    response = requests.post(url, json=playload, headers=headers, verify=False)
    assert response.status_code in  (200, 201), "Ошибка аутентификации BMC"
    assert "X-Auth-Token" in response.headers, "Токен аутентификации не найден в заголовках ответа"
    logger.info("Вход в BMC выполнен успешно")

def test_get_info_session(autentification_Bmc):
    url = f"https://{URL}/redfish/v1/Systems/system"
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": autentification_Bmc
    }
    response = requests.get(url, headers=headers, verify=False)
    assert response.status_code == 200, "Ошибка получения информации о сессии"
    data = response.json()
    assert "Status" in data, "Поле 'Status' отсутствует в ответе"
    assert "PowerState" in data, "Поле 'PowerState' отсутствует в ответе"
    logger.info("Информация о сессии получена успешно")
    
def test_on_off_server(autentification_Bmc):
    url = f"https://{URL}/redfish/v1/Systems/system/Actions/ComputerSystem.Reset"
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": autentification_Bmc
    }
    payload_on = {
        "ResetType": "On"
    }
    payload_off = {
        "ResetType": "ForceOff"
    }
    
    response_off = requests.post(url, json=payload_off, headers=headers, verify=False)
    time.sleep(2)
    assert response_off.status_code in (200, 202, 204), "Ошибка выключения сервера"
    response_on = requests.post(url, json=payload_on, headers=headers, verify=False)
    assert response_on.status_code in (200, 202, 204), "Ошибка включения сервера"
    time.sleep(2)
    logger.info("Сервер успешно выключен и включен")

def test_CPU_temperature(autentification_Bmc):
    url = f"https://{URL}/redfish/v1/Chassis/chassis/ThermalSubsystem/ThermalMetrics"
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": autentification_Bmc
    }
    response = requests.get(url, headers=headers, verify=False)
    assert response.status_code == 200, "Ошибка получения информации о температуре CPU"
    data = response.json()
    temperatures = data.get("TemperatureReadingsCelsius", [])
    cpu_temps = [temp for temp in temperatures if "CPU" in temp.get("Name", "")]
    
    if not cpu_temps:
        logger.warning("Информация о температуре CPU не найдена")
        pytest.skip("Информация о температуре CPU не найдена")
        
    for cpu in cpu_temps:
        current_temp = cpu.get("ReadingCelsius")
        assert current_temp is not None, f"Текущая температура для {cpu.get('Name')} не найдена"
        assert 0 <= current_temp <= 100, f"Температура {cpu.get('Name')} вне допустимого диапазона: {current_temp}°C"
        logger.info(f"Температура {cpu.get('Name')}: {current_temp}°C")