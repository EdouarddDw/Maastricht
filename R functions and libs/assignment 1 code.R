


library(datasauRus)
library(tidyverse)


#exercice 3

#create dataset and quick overview
my_data <- datasaurus_dozen
#view(my_data)
head(my_data)
summary(my_data)

# 1)
# get each stat for each of the datasets
stats <- my_data %>%
  group_by(dataset) %>%
  summarise(
    mean_x = mean(x),
    mean_y = mean(y),
    sd_x = sd(x),
    sd_y = sd(y),
    correlation = cor(x, y)
  )
#print all stats in a table format
print(stats)




# 2)
#plot x and y for each dataset
ggplot(datasaurus_dozen, aes(x = x, y = y)) + 
  geom_point() +
  facet_wrap(~ dataset, scales = "free") +    # Create separate plots for each dataset
  theme_minimal() +
  labs(title = "Scatterplots of x vs y in Datasaurus Dozen", 
       x = "X value", 
       y = "Y value") 


# exercice 4

library(gapminder)
#finding the data set
my_data <- gapminder

# 2)
#view(my_data)
head(my_data)

# 3)
avg_life_expectancy <- my_data %>%
  group_by(continent, year) %>%
  summarise(average_lifeExp = mean(lifeExp))
print(avg_life_expectancy)


# 4)


gapminder_stats_across <- my_data %>%
  group_by(year) %>%
  summarise(
    across(c(lifeExp, pop, gdpPercap),
           list(max = max, min = min, mean = mean))
  )

print(gapminder_stats_across)
#view(gapminder_stats_across)

# 5)
highest_life_expectancy <- my_data %>%
  group_by(year, continent) %>%
  slice_max(order_by = lifeExp, n = 1)

print(highest_life_expectancy)

# 6)
#find what 1% of the sample represents
sample_size <- round(nrow(my_data) * 0.01)

# create a random sample representing 1% of all observations
random_sample <- my_data %>%
  slice_sample(n = sample_size)

# View the results
print(random_sample)

# 7)
# Rename the lifeExp variable to "life_expectancy"
gapminder_renamed <- my_data %>%
  rename(life_expectancy = lifeExp)

# View the results
head(gapminder_renamed)


# 8)
# Use pivot_longer to combine life expectancy, population, and GDP per capita into a single variable
gapminder_long <- my_data %>%
  pivot_longer(
    cols = c(lifeExp, pop, gdpPercap),
    names_to = "variable",
    values_to = "value"
  )

# View the results
head(gapminder_long)




