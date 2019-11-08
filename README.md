# Introduction to the Open Solar Furnace

When people think of solar panels, the image that often comes to mind is of [photovoltaic panels](https://en.wikipedia.org/wiki/Photovoltaics) which convert the sun's energy into electricity to power homes (and maybe to charge an electric vehicle). While photovoltaics are essential for transitioning to a renewable energy economy, they are still quite expensive and remain out of reach for the majority of homeowners. While some enthusiasts may be able to save money by installing their own photovoltaic systems, for most people, the technology is too complicated and requires installation by a trained professional.

Solar heating represents a much simpler technology that is easy to understand, build, and install by anyone who is handy around the house. And because typical Canadian/US homes use 40-60% of their energy for space heating (and an additional ~20% for water heating)[[1], [2], [3]], solar heating represents an even greater opportunity relative to photovoltaics for reducing energy cost and greenhouse gas emissions within the home.

Compared to photovoltaics, solar heating requires a much lower initial investment. There are several [off-the-shelf hot air systems](https://gitlab.com/ryanfobel/open-solar-furnace/wikis/off-the-shelf-systems) available for a few thousand dollars and [many DIY projects](https://gitlab.com/ryanfobel/open-solar-furnace/wikis/DIY-systems) can be made for a few hundred dollars using scrap and/or recycled materials (e.g., [aluminum pop cans](https://www.freeonplate.com/examples-of-diy-solar-panels/)). Open collaboration and sharing is already common within the DIY solar community (e.g., sharing of build videos and documentation), but most existing projects tend to be built as one-offs, and none are explicitly shared as [open-source hardware](https://en.wikipedia.org/wiki/Open-source_hardware) / [software](https://en.wikipedia.org/wiki/Open-source_software). While this distinction may seem trivial, it is important. The open-source philosophy has been [incredibly successful](https://www.wired.com/2016/08/open-source-won-now/) in the world of software (most web and mobile platforms are at least partly built using open-source code) and a growing movement seeks to apply these same principles to hardware development. Open-source development (including licensing and a commitment to [best practices established by the community](https://www.oshwa.org/sharing-best-practices/)) provides a framework that encourages people to collaboratively solve problems, test and compare alternatives, and should ultimately produce better designs that are more reproducible and scalable. When successful, open-hardware communities bring added visibility to an idea and help support a robust ecosystem of hobbyists, academic researchers, and commercial enterprises as evidenced by the explosive growth around 3D printing after the launch of the [RepRap project](https://en.wikipedia.org/wiki/RepRap_project).

# Goals for this project:

The goal of this project is to create a solar heater design (or collection of designs) that achieve the following:

1. Low-cost
2. Easy-to-build
3. Made with materials that are widely available
4. Measure/track the performance/efficiency

We plan to draw upon existing designs published online to meet the first 3 design requirements, and to add a simple WiFi-enabled microcontroller (e.g., [ESP8266](https://en.wikipedia.org/wiki/ESP8266) or [ESP32](https://en.wikipedia.org/wiki/ESP32)) to facilitate performance tracking and thermostat control. This will allow the community to evaluate/test design alternatives (e.g., [A/B testing](https://en.wikipedia.org/wiki/A/B_testing)) and to track the overall impact of these solar heaters in reducing heating costs and carbon emissions at an individual and community level.

# Project status (updated Aug 8, 2019)

We built a small (2'x4') prototype and hosted a [build party](https://photos.app.goo.gl/3FedmAXnWcR5EEUT7) in March to assemble a full-sized panel (4'x8') with a team of 6 people. This panel is currently being installed on my home as a demonstration.

![Prototype](https://gitlab.com/ryanfobel/open-solar-furnace/wikis/uploads/f3c4464e2cd495b67126fe4544281fc0/image.png)
![Build party](https://gitlab.com/ryanfobel/open-solar-furnace/wikis/uploads/978fbffa4fab1c8f74f3b16f2da31182/image.png)

[Rise Waterloo Region](https://www.facebook.com/risewaterlooregion/) will host a community build workshop in Kitchener-Waterloo in the Fall of 2019. If you'd like to learn more or to be notified of upcoming workshops, please get in touch via email at risewaterlooregion@gmail.com.

![Rise Waterloo Region](https://gitlab.com/ryanfobel/open-solar-furnace/wikis/uploads/c18c53d37defcee7939215fca3499d04/image.png)

# More information:

* [Estimating costs and benefits](https://gitlab.com/ryanfobel/open-solar-furnace/wikis/Estimating-costs-and-benefits)
* [Build instructions](https://gitlab.com/ryanfobel/open-solar-furnace/wikis/Build-instructions)
* [Solar heating theory and design tips](https://gitlab.com/ryanfobel/open-solar-furnace/wikis/Solar-heating-theory-and-design-tips)
* [List of off-the-shelf systems](https://gitlab.com/ryanfobel/open-solar-furnace/wikis/off-the-shelf-systems)
* [List of DIY systems](https://gitlab.com/ryanfobel/open-solar-furnace/wikis/DIY-systems)

# Support

This project is supported by [Life Co-op's Community fund](http://www.lifecoop.ca/lifes-community-fund) and a [City of Kitchener community grant](https://www.kitchener.ca/en/city-services/community-grants.aspx).

![Life Co-op logo](https://gitlab.com/ryanfobel/open-solar-furnace/wikis/uploads/31845e7600df52725a43f774fb5dab4e/image.png).
![City of Kitchener Logo](https://gitlab.com/ryanfobel/open-solar-furnace/wikis/uploads/adfa5804a64cb85f40aac0540dd048d6/image.png)

[1]: https://www.eia.gov/todayinenergy/detail.php?id=10271
[2]: https://www.hydroone.com/saving-money-and-energy/residential/tips-and-tools/home-heating-guide
[3]: http://www.hydroquebec.com/residential/customer-space/electricity-use/electricity-consumption-by-use.html