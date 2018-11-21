# Introduction

When most people think about solar panels, the image that comes to mind is of [photovoltaic panels](photovoltaics) which convert the sun's energy into electricity to power homes (and maybe to charge an electric vehicle). While photovoltaics are essential for transitioning to a renewable energy economy, they are still quite expensive and remain out of reach to many homeowners. While some enthusiasts may be able to save money by installing their own photovoltaic systems, for most homeowners, the technology is too complicated and requires installation by a trained professional.

Solar furnaces represent a much simpler technology that is easy to understand, build, and install by anyone who is handy around the house. And because typical Canadian/US homes use 40-60% of their energy for heating (and an additional ~20% for water heating)[[1], [2], [3]], solar furnaces represent an even greater opportunity relative to photovoltaics for reducing energy cost and greenhouse gas emissions within the home.

Compared to photovoltaics, solar furnaces require a much lower initial investment. There are several commercially available systems available for a few thousand dollars, and DIY projects can be made for a few hundred dollars using scrap and/or recycled materials (e.g., [aluminum pop cans](https://www.freeonplate.com/examples-of-diy-solar-panels/)). While a number of DIY projects are available online and many include detailed written and video tutorials, none of these projects are explicitly presented as [open-source hardware] (i.e., with a license and an open invitation and protocol for the community to improve/iterate on the design). While this distinction may seem trivial, it is important. By explicitly publishing a project as open-source hardware, it encourages communities to work together to solve problems, test and compare design alternatives, and should ultimately produce a better design that is more reproducible and scalable. An open-hardware community can also help to bring added visibility to a technology or idea, which can help support a robust ecosystem of hobbyists, academic researcher, and commercial enterprises as evidenced by the explosive growth around 3D printing after the launch of the [RepRap project](https://en.wikipedia.org/wiki/RepRap_project).

# Goals for this project:

The goal of this project is to create a solar furnace design (or collection of designs) that achieve the following:

1. low cost
2. easy to build
3. made with materials that are widely available
4. measure/track the performance/efficiency

We plan to draw upon existing designs published online to meet the first 3 design requirements, and to add a simple WiFi-enabled microcontroller (e.g., [ESP8266](https://en.wikipedia.org/wiki/ESP8266) or [ESP32](https://en.wikipedia.org/wiki/ESP32)) to facilitate performance tracking and thermostat control. This will allow the community to evaluate/test design alternatives (e.g., A/B testing) and to track the overall impact of these solar furnaces in reducing heating costs and carbon emissions at an individual and community level.

For more information, please see the [wiki](https://gitlab.com/ryanfobel/open-solar-furnace/wikis/home).


[1]: https://www.eia.gov/todayinenergy/detail.php?id=10271
[2]: https://www.hydroone.com/saving-money-and-energy/residential/tips-and-tools/home-heating-guide
[3]: http://www.hydroquebec.com/residential/customer-space/electricity-use/electricity-consumption-by-use.html
[photovoltaics]: https://en.wikipedia.org/wiki/Photovoltaics
[open-source hardware]: https://en.wikipedia.org/wiki/Open-source_hardware