# Feature Requests

Not all features have been implemented for download.  This is a running list of things which don't exist yet but someone might be interested in

* ~~Download Flat Rate Manual for your VIN - https://techinfo.toyota.com/t3Portal/appmanager/t3/frm?titleDetails=frm&vin1=JTMHY7AJ6Dxxxxxxx#~~ (Done without a VIN: tis-frm.py saves it by division/model/year for every VDS)
* Get Vehicle information for your VIN (Production Date, Engine #, standard equipment, etc) - https://techinfo.toyota.com/t3Portal/appmanager/t3/ti?_nfpb=true&_windowLabel=vinSearch_2&vinSearch_2_actionOverride=%2Fportlets%2Ftis%2FvinSearch%2FvinLookup&_pageLabel=t3_veh_inq_vin_page
* ~~Fluid capacities - https://techinfo.toyota.com/t3Portal/FluidSpecificationsServlet?MODEL=Land%20Cruiser&YEAR=2013&VDS=HY7AJ&lang=en (is VDS required?)~~ (Done another way: the servlet, and SpecificationServlet for vehicle specs, only work after a VIN lookup in the same session, which counts against a daily limit.  The repair manual has the capacities on its SPECIFICATIONS ... SERVICE DATA pages, and the owner's manual (dl-ref.sh) too; the front page now lists them under Fluid Capacities.  Could still save TIS's own charts if the user gives a VIN.)
* ~~Download Service Bulletins and Tech Tips (PDFs, but how do we get the list? The list returned is ALL vehicles, not just our model)~~ (Done: dl-bulletins.sh, from the Service Information search's SB/TT tab for the vehicle; USA ones, without the obsolete)
* Download Quick Training Guides (PDFs, but how do we get the list? These are not vehicle specific)
* ~~Download Service Campaigns (PDFs, but how do we get the list? The list returned is ALL vehicles, not just our model)~~ (Done: dl-bulletins.sh, from the SC tab)
* Download Accessory Docs (PDFs, but how do we get the list? The list returned is ALL vehicles, not just our model)
* ~~Owners Manual, Maintenance Schedule, Accessory/Nav owners manuals (under Reference Information tab)~~ (Done: dl-ref.sh)
* ~~Technician's References (under Reference Information tab)~~ (Done: dl-ref.sh)
* ~~"Warranty and Claims Processing" provides PDFs of the Flat Rate Manual~~ (Done: the older, to about 2015, Flat Rate Manuals with dl-ref.sh, newer ones from the FRM application with tis-frm.py)
* Service Operations/Parts provides "ASM and Parts Professional Reference" with Towing Specs, Fluids, (Partly done: dl-ref.sh downloads the ASM pages TIS lists for the vehicle, ie: General Vehicle Information and the engine oil chart)

* Toyota Technical Training Guide downloads are generic, not for a specific vehicle, but might be desirable.

# Known Bugs or Desirable Changes
Most of the tools generate a lot of output.  That output often is not captured or error checked.
* All output should be logged  (Done: every script also appends its output to $DOWNLOAD_TO/tis-clone.log, see tis-log.sh)

There are a lot of steps in the [HOWTO.md](HOWTO.md) file.
* ~~Setup should also test for dependencies and try to remediate/install or at least warn the user they have work to do before getting started.~~ (Done: setup.sh lists everything missing with the install command for apt/dnf/pacman/zypper/brew and offers to run it)
* The first few steps to log in and make any config changes should be guided
* It would be better if we could just prompt the user with the vehicle division/model/year like the website does and handle EVERYTHING based on that input
  * ~~A tis-lookup.py that asks for Make, Model and Year (like the TIS search page) and prints the 5-character code~~ (Done: tis-lookup.py)
  * ~~tis-clone runs tis-lookup.py when no code is given instead of failing, and also runs dl-ref.sh with the same make, model and year~~ (Done)
