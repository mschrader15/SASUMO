from importlib.metadata import distribution
import os
from typing import Any, Iterable, List, Tuple, Generator
from xml.dom import minidom

from sumolib.vehicletype import (
    CreateVehTypeDistribution,
    VehAttribute,
    _DIST_DICT,
)
from sumolib.files.additional import write_additional_minidom
from omegaconf import DictConfig

#  Internal imports
from SASUMO.utils.sumo_dist_builder import create_distribution
from SASUMO.utils.constants import TEMP_PATTERN, SUMO_HOME


DIST_ARG_HELPER = {
    "uniform": ("a", "b"),
    "normal": ("mu", "sd"),
    "normalCapped": ("mu", "sd", "min", "max"),
    "lognormal": ("mu", "sd"),
    "gamma": ("alpha", "beta"),
}


def _parse_dist_params(dist: str) -> Tuple[float]:
    dist_name = dist.split("(")[0]
    inner = dist.split("(")[-1].split(")")[0]
    return dict(
        zip(
            DIST_ARG_HELPER[dist_name],
            map(lambda x: float(x.strip()), inner.split(",")),
        )
    )


def _parse_dist_bounds(bounds: str) -> Tuple[float]:
    inner = bounds.split("[")[-1].split("]")[0]
    return tuple(map(lambda x: float(x.strip()), inner.split(",")))


def _dist_line_parser(line: str) -> VehAttribute:
    split = tuple(x for x in map(lambda x: x.strip(), line.split(";")) if x)
    is_param = split[0] == "param"
    i = 0 + is_param
    is_dist = split[i + 1].split("(")[0] in _DIST_DICT.keys()
    params = {
        "name": split[i],
        "is_param": is_param,
        "distribution": split[i + 1].split("(")[0] if is_dist else None,
        "distribution_params": _parse_dist_params(split[i + 1]) if is_dist else None,
        "bounds": _parse_dist_bounds(split[i + 2])
        if len(split) > (2 + i) and is_dist
        else None,
        "attribute_value": None if is_dist else split[i + 1],
    }
    return VehAttribute(**params)


def create_veh_distributions(
    args: Iterable[DictConfig],
    output_file_name: os.PathLike,
    distribution_size: int,
    distribution_name: str,
    seed: int,
) -> None:
    """
    Creates a vehicle distribution file representing a
    """
    xml_dom = minidom.Document()

    # create the vehicle distribution
    vtype_dist_node = xml_dom.createElement("vTypeDistribution")
    vtype_dist_node.setAttribute("id", distribution_name)

    for type_group in args:
        # get the composition percentage
        comp_percentage = eval(str(type_group.get("fleet_composition", "1")))
        #
        dist = CreateVehTypeDistribution(
            seed=seed,
            size=int(distribution_size * comp_percentage),
            name=type_group.vehicle_name,
            resampling=3,
            decimal_places=3,
        )

        vary_lines = []
        devices = []
        for var in type_group.get("variable_parameters", []):
            # create the device handler
            if var.get("device", False):
                devices.append(
                    (var.get("variable_name"), var.get("device_value"), var.get("val"))
                )
            else:
                dist_func = create_distribution(var.distribution.type)
                sumo_dist_string = dist_func(
                    val=var.val, **dict(var.distribution.params)
                )
                vary_lines.append(f"{var.variable_name};{sumo_dist_string}")

        for line in (
            vary_lines + type_group.get("distribution_parameters", "").splitlines()
        ):
            if "#" not in line:
                dist.add_attribute(_dist_line_parser(line))

        for i in range(dist.size):
            veh_type_node = xml_dom.createElement("vType")
            veh_type_node.setAttribute("id", dist.name + str(i))
            dist._generate_vehType(xml_dom, veh_type_node)
            vtype_dist_node.appendChild(veh_type_node)

        # apply the device handlers
        for device in devices:
            _apply_device_params(
                device[0], device[1], device[2], vtype_dist_node, xml_dom
            )

    # write the file to XML
    write_additional_minidom(xml_dom, vtype_dist_node, output_file_name)


def _apply_device_params(
    param_name: str,
    param_value: Any,
    prob: float,
    vtype_dist_node: minidom.Element,
    xml_dom: minidom.Document,
) -> str:
    """
    Applies the distribution parameters to the vehicle type
    """
    # doing this because it has already been seeded.
    from sumolib.vehicletype import random

    for node in vtype_dist_node.childNodes:
        if random.random() <= prob:
            param_node = xml_dom.createElement("param")
            param_node.setAttribute("key", param_name)
            value = str(
                param_value if isinstance(param_value, float) else eval(param_value)
            )
            param_node.setAttribute("value", value)
            node.appendChild(param_node)


def correlated_sumo_dist_builder(
    args: Iterable[DictConfig],
    output_file_name: os.PathLike,
    distribution_size: int,
    distribution_name: str,
    seed: int,
) -> None:
    """
    Creates a correlated vehicle distribution file. Hardcoded for time being, cause the paper is due shortly.
    """
    import numpy as np
    from numpy.random import default_rng
    import math

    multivariate_normal = default_rng(seed=int(seed)).multivariate_normal

    def to_lognormal(mu, sd):
        lns = math.sqrt(math.log(sd / mu) ** 2 + 1)
        lnmu = math.log(mu) - 0.5 * math.log((sd / mu) ** 2 + 1)
        return lnmu, lns

    mean = [
        to_lognormal(1.406, 1.012)[0],
        to_lognormal(2.225, 1.849)[0],
        to_lognormal(2.172, 1.152)[0],
        1.266,
    ]

    cov = [
        [to_lognormal(1.406, 1.012)[1], 0.347, 0.25, -0.187],
        [0.347, to_lognormal(1.406, 1.849)[1], 0.037, -0.144],
        [0.25, 0.037, to_lognormal(2.172, 1.152)[1], -0.207],
        [-0.187, -0.144, -0.207, 0.507],
    ]

    xml_dom = minidom.Document()

    # create the vehicle distribution
    vtype_dist_node = xml_dom.createElement("vTypeDistribution")
    vtype_dist_node.setAttribute("id", distribution_name)

    for type_group in args:
        # get the composition percentage
        comp_percentage = eval(str(type_group.get("fleet_composition", "1")))
        #
        dist = CreateVehTypeDistribution(
            seed=seed,
            size=int(distribution_size * comp_percentage),
            name=type_group.vehicle_name,
            resampling=3,
            decimal_places=3,
        )

        vary_lines = []
        devices = []
        #  This should be empty for now
        for var in type_group.get("variable_parameters", []):
            # create the device handler
            if var.get("device", False):
                devices.append(
                    (var.get("variable_name"), var.get("device_value"), var.get("val"))
                )
            else:
                dist_func = create_distribution(var.distribution.type)
                sumo_dist_string = dist_func(
                    val=var.val, **dict(var.distribution.params)
                )
                vary_lines.append(f"{var.variable_name};{sumo_dist_string}")

        for line in (
            vary_lines + type_group.get("distribution_parameters", "").splitlines()
        ):
            if "#" not in line:
                dist.add_attribute(_dist_line_parser(line))

        for i in range(dist.size):
            veh_type_node = xml_dom.createElement("vType")
            veh_type_node.setAttribute("id", dist.name + str(i))
            dist._generate_vehType(xml_dom, veh_type_node)

            # add in the correlated parameters. This is bad code, but it works for now.
            while True:
                res = multivariate_normal(
                    mean=mean,
                    cov=cov
                    # size=10000
                )
                res[:3] = np.exp(res[:3])
                if all(res > 0.2) and all(res[:2] < 8) and res[2] < 5 and res[3] < 3:
                    break

            for param_name, param_value in zip(
                ["accel", "decel", "minGap", "tau"], res
            ):
                veh_type_node.setAttribute(param_name, str(param_value))

            vtype_dist_node.appendChild(veh_type_node)

        # apply the device handlers
        for device in devices:
            _apply_device_params(
                device[0], device[1], device[2], vtype_dist_node, xml_dom
            )

    # write the file to XML
    write_additional_minidom(xml_dom, vtype_dist_node, output_file_name)
