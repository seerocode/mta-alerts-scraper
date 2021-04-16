# MTA Alerts - Escalator and Elevator Outages

This scraper was built to collect MTA alerts escalator and elevator outage data from 2018 to 2020. This data was scraped from the [MTA Alerts Archive](https://mymtaalerts.com/archive).

Gothamist writes that only approximately 25% of the MTA's 472 subway stations are accessible with plans to make all stations 100% accessible by 2034. The data collected with this scraper will be used to explore the impact escalator and elevator outages have had across the MTA subway system.

Keeping in mind that if an elevator/escalator is down in a train station that means it may only be partially or completely innaccessible if there are no alternatives during the outage.

📝**NOTE:** *Elevator/escalator service alerts were only released starting 2018.*

## Project Status

This research is currently in progress.

**To-do:**

- [x] 📔 Scrape MTA escalator and elevator outage alerts
- [x] 🧹 Standardize alerts data to include elevator/escalator ID
- [x] 🔪 Extract station names for each row in the collected outage data 
- [ ] 🚊 Merge ridership numbers from [turnstile data](http://web.mta.info/developers/turnstile.html) to explore possible connections between ridership and outages
- [ ] ⏱ Derive "time to repair" from each outage to understand how long an escalator/elevator remained out of service (in total, on average, per station, etc.)
- [ ] 🧱 Merge census data (demographics) for neighborhoods where these train stations are located
- [ ] 📊 Summary statistics and exploration
- [ ] 📍 Create map of where outages were experienced and which stations experience the longest average outages over time
- [ ] 🪄 Further analysis (TBD as research evolves)

## Installation and Setup Instructions

### R Markdown Notebook

If you want to jump straight into the data, download RStudio desktop from [here](https://www.rstudio.com/products/rstudio/download/#download) if you don't have it already and open the `mta-alerts.Rmd` notebook in the `analysis` directory to run the notebook with the data for outages.

Alternatively, you can open the CSV file in your preferred CSV editor but be warned that it is 220,000+ rows of data.

### Scraper

📝**NOTE:** *The required data for this project has already been scraped and is available in the `analysis` directory as well as back up database files in the `db-backup` directory. The scraper is intentionally slow to prevent your IP from getting blocked. Each request lasts anywhere between 35 and 45 seconds and therefore should take about **24 hours** to scrape a year's worth of data.*

If you'd like to scrape the data yourself locally, follow these instructions:

#### Prerequisites (scraper)

- `python3` - This [guide](https://realpython.com/installing-python/) is pretty comprehensive for all systems.
- `pip` - Should already be installed if you have python but [here are the docs](https://pip.pypa.io/en/stable/installing/) in case it's not.
- `git lfs` - You'll need this if you'll be committing any large db or csv files as tracked in the `.gitattributes` file. You can install from [here](https://git-lfs.github.com/) and run `git lfs install` after.
- `docker` - Optional for running locally and necessary for running in a virtual machine

#### Install and run (MacOS instructions)

1. Clone this repo (or fork the repo and clone from your fork)

   ```bash
   git clone https://github.com/seerocode/mta-alerts-scraper.git
   ```

2. Change directory into the folder and create a virtual environment

   ```bash
   cd mta-alerts-scraper
   python3 -m venv venv
   ```

3. Run virtual environment

   ```bash
   source venv/bin/activate
   ```

4. Install required modules

   ```bash
   pip install -r requirements.txt
   ```

5. Choose a year to scrape data for (*2018 and beyond*) and run the scraper with that year as an argument

   ```bash
   python3 scraper.py 2018
   ```

You should see logs generated in a new `app.log` file and a progress bar in your terminal.

#### Install and run (Linux virtual machine instructions)

I strongly recommend that if you **MUST** run this scraper, that you do so on a virtual machine. There is no continue option in this scraper so you can't currently scrape from a page you left off at if the script fails. I welcome you to open a PR to change that!

1. Confirm that you have Docker, Python, and pip installed on your virtual machine.

2. SSH into your machine and follow steps 1-4 from the above instructions for MacOS install

3. Choose a year to scrape data for (*2018 and beyond*) and run the scraper with that YEAR as a Docker build argument

   ```bash
   docker build --build-arg YEAR=2018 -t mta-alerts .
   ```

4. Run the docker container and mount a volume to commit the generated database file later

   ```bash
   docker run -it -v ${PWD}:/app/db  mta-alerts
   ```

Your docker container should now be running the scraper. If you need to detatch from the container in your VM without stopping it, press `CTRL+P` followed by `CTRL+Q`. To reattach to the container and check its progress, run `docker attach mta-alerts`. If that fails, run `docker ps` to see the running containers, copy the container ID, and run `docker attach <container_id>`.
