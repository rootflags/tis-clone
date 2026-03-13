# Feature Requests

Not all features have been implemented for download.  This is a running list of things which don't exist yet but someone might be interested in

* Download Flat Rate Manual for your VIN - https://techinfo.toyota.com/t3Portal/appmanager/t3/frm?titleDetails=frm&vin1=JTMHY7AJ6Dxxxxxxx#
* Get Vehicle information for your VIN (Production Date, Engine #, standard equipment, etc) - https://techinfo.toyota.com/t3Portal/appmanager/t3/ti?_nfpb=true&_windowLabel=vinSearch_2&vinSearch_2_actionOverride=%2Fportlets%2Ftis%2FvinSearch%2FvinLookup&_pageLabel=t3_veh_inq_vin_page
* Fluid capacities - https://techinfo.toyota.com/t3Portal/FluidSpecificationsServlet?MODEL=Land%20Cruiser&YEAR=2013&VDS=HY7AJ&lang=en (is VDS required?)
* Download Service Bulletins and Tech Tips (PDFs, but how do we get the list? The list returned is ALL vehicles, not just our model)
* Download Quick Training Guides (PDFs, but how do we get the list? These are not vehicle specific)
* Download Service Campaigns (PDFs, but how do we get the list? The list returned is ALL vehicles, not just our model)
* Download Accessory Docs (PDFs, but how do we get the list? The list returned is ALL vehicles, not just our model)
* Owners Manual, Maintenance Schedule, Accessory/Nav owners manuals (under Reference Information tab)
* Technician's References (under Reference Information tab)
* "Warranty and Claims Processing" provides PDFs of the Flat Rate Manual
* Service Operations/Parts provides "ASM and Parts Professional Reference" with Towing Specs, Fluids, 

* Toyota Technical Training Guide downloads are generic, not for a specific vehicle, but might be desirable.

# Known Bugs or Desirable Changes
Most of the tools generate a lot of output.  That output often is not captured or error checked.
* All output should be logged
* All output should be reviewed for errors.  Ideally we'd have a tool which provides a failure report and also a way to re-run against failed pages.
* Output to the terminal should be limited to "URL [RESULT]" instead of the full wget (or other tool) output

There are a lot of steps in the [HOWTO.md](HOWTO.md) file.
* Setup should also test for dependencies and try to remediate/install or at least warn the user they have work to do before getting started.
* The first few steps to log in and make any config changes should be guided
* Everything else should really be a single command that runs all the download tasks and then runs all the website and PDF creation tasks
* It would be better if we could just prompt the user with the vehicle division/model/year like the website does and handle EVERYTHING based on that input

Overall better error handling would be helpful
* We now test for whether we're correctly logged in, though that could be better, however...
* We don't test if we got logged out along the way so it's possible for the first few pages to succeed but then a whole bunch fail to download correctly
