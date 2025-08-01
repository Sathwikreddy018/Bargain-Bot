library(DBI)
library(RMariaDB)
library(ggplot2)
library(lubridate)

con <- dbConnect(RMariaDB::MariaDB(),
                 user = "BargainBot",
                 password = "%BargainBot",
                 dbname = "manuel projekt v4",
                 host = "localhost")

data <- dbGetQuery(con, "
  SELECT useruser_id, timestamp
  FROM shoppinglist
")

dbDisconnect(con)

data$weekday <- wday(as.Date(data$timestamp), label = TRUE, abbr = FALSE, week_start = 1)
data <- subset(data, as.Date(timestamp) >= as.Date("2024-08-01"))

summary <- aggregate(timestamp ~ weekday, data = data, FUN = length)
colnames(summary) <- c("weekday", "shopping_list_count")

ggplot(summary, aes(x = weekday, y = shopping_list_count)) +
  geom_col(fill = "steelblue") +
  geom_text(aes(label = shopping_list_count), vjust = -0.3, size = 3) +
  labs(title = "Created Shopping Lists by Weekday",
       x = "Weekday", y = "Number of Shopping Lists") +
  theme_minimal() +
  theme(plot.title = element_text(face = "bold", hjust = 0.5))
