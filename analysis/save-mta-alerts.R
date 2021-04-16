library(DBI)
library(tidyverse)
library(lubridate)
library(stringr)

## Connect to db
con <- dbConnect(drv=RSQLite::SQLite(), dbname="alerts.db")

alerts <- dbReadTable(con, "mtaalerts")
alerts <- select(alerts, -c(index, Agency))

alerts <- alerts %>%
  mutate(Message.Id = as.integer(Message.Id) ) %>%
  mutate(Date = mdy_hm(Date)) %>%
  mutate(elevator_escalator_id = str_match(Message, "((EL|ES)\\d{2,3}(X|x)?)")[,2]) %>%
  mutate(is_out_of_service = grepl('outage|Outage', Subject)) %>%
  relocate(elevator_escalator_id, is_out_of_service)
alerts

write.csv(alerts,"alerts.csv", row.names = FALSE)
