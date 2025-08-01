library(DBI)
library(RMariaDB)
library(ggplot2)
library(lubridate)

user_id <- 8 # <- Select user ID

con <- dbConnect(RMariaDB::MariaDB(),
                 user = "BargainBot",
                 password = "%BargainBot",
                 dbname = "manuel projekt v4",
                 host = "localhost")

data <- dbGetQuery(con, sprintf("
  SELECT s.timestamp, c.categoryname, ps.amount
  FROM shoppinglist s
  JOIN product_shoppinglist ps ON s.shoppinglist_id = ps.shoppinglistshoppinglist_id
  JOIN product p ON ps.productproduct_id = p.product_id
  JOIN productcategory c ON p.productcategoryproductcategory_id = c.productcategory_id
  WHERE s.useruser_id = %d
", user_id))

dbDisconnect(con)

data$month <- floor_date(as.Date(data$timestamp), unit = "month")
data <- subset(data, month >= as.Date("2024-08-01"))

summary <- aggregate(amount ~ month + categoryname, data = data, FUN = sum)

ggplot(summary, aes(x = month, y = amount, color = categoryname)) +
  geom_line(size = 0.75) +
  geom_point(size = 1) +
  scale_x_date(date_breaks = "month", date_labels = "%b %Y") +
  labs(title = paste("Product Quantity per Month and Category (user_id =", user_id, ")"),
       x = "Month", y = "Purchased Quantity", color = "Category") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45),
        plot.title = element_text(face = "bold", hjust = 0.5))
