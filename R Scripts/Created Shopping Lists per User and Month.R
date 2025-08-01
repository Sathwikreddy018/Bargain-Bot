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

data$timestamp <- as.Date(data$timestamp)
data$month <- floor_date(data$timestamp, "month")
data <- subset(data, month >= as.Date("2024-08-01") & month <= as.Date("2025-05-31"))

summary <- aggregate(timestamp ~ month + useruser_id, data = data, FUN = length)
colnames(summary) <- c("month", "user_id", "count")

ggplot(summary, aes(x = month, y = count, color = as.factor(user_id))) +
  geom_line(size = 0.75) +
  geom_point(size = 1) +
  scale_x_date(date_breaks = "1 month", date_labels = "%b %Y") +
  scale_y_continuous(breaks = 0:ceiling(max(summary$count))) +
  labs(title = "Created Shopping Lists per User and Month",
       x = "Month", y = "Number of Shopping Lists", color = "User ID") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        plot.title = element_text(face = "bold", hjust = 0.5))
