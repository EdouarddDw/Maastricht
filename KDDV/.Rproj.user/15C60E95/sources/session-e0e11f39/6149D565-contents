#import dataset and libraryes
BankDeposit <- read.csv("~/GitHub/Maastricht/KDDV/Take at home exam/BankDeposit.csv", stringsAsFactors=TRUE)

library(tidyverse)
library(moments)
library(kableExtra)
library(outliers)
library(rpart)
library(caret)



head(BankDeposit)
summary(BankDeposit)

#random subset
set.seed(16)
my_data <- BankDeposit[sample(nrow(BankDeposit), size = 5000),]

#missing data
missing_values <- sapply(my_data, function(x) sum(is.na(x)))
missing_values #no missing data :)

#data understanding
head(my_data)
summary(my_data)

numeric_data <- select_if(my_data, is.numeric)
numeric_data

num_cols <- ncol(numeric_data)
num_cols


# initiate some empty vectors in which we can contain our descriptive statistics
s.min = s.max = s.mean = s.med = s.qf = s.qt = s.range = s.iqr = s.skew = c()

# Create a for loop in which it calculates all of the different statistics we are interested in
# You can definitly use the summarise() function from dplyr...
for (i in 1:7) {
  s.min = c(s.min, min(numeric_data[,i]))
  s.max = c(s.max, max(numeric_data[,i]))
  s.range = c(s.range, s.max[i]-s.min[i])
  s.mean = c(s.mean, mean(numeric_data[,i]))
  s.med = c(s.med, median(numeric_data[,i]))
  s.qf = c(s.qf, quantile(numeric_data[,i],0.25))
  s.qt = c(s.qt, quantile(numeric_data[,i],0.75))
  s.iqr = c(s.iqr, IQR(numeric_data[,i]))
  s.skew = c(s.skew, skewness(numeric_data[,i]))
}

# Combine the vectors of descriptive statistics 
stats = rbind.data.frame(s.min, s.max, s.mean, s.med, s.qf, s.qt, s.range, s.iqr,s.skew)
# Insert the row names
rownames(stats) = c("Minimum", "Maximum", "Mean", "Median", "1st Quartile", "3rd Quartile", "Range", "IQR","Skewness")
# Insert the same column names from the data frame
colnames(stats) = colnames(numeric_data)

# Display the table
stats %>% kbl() %>% kable_minimal()


#outliers
#numericaly

#Zscore
zscores = sapply(numeric_data[,1:7],FUN = scale)
outliers <-which(zscores > 3 | zscores < -3, arr.ind = T)
str(outliers)
#500 outliers using the Z score

#IQR method
outlier_check <- sapply(numeric_data, outlier)
outlier_check

#extreme outlier check
find_extreme_outliers <- function(x) {
  q1 <- quantile(x, 0.25, na.rm = TRUE)
  q3 <- quantile(x, 0.75, na.rm = TRUE)
  iqr <- q3 - q1
  lower_bound <- q1 - 3 * iqr
  upper_bound <- q3 + 3 * iqr
  x < lower_bound | x > upper_bound
}

find_extreme_outlier_count <- function(x) {
  q1 <- quantile(x, 0.25, na.rm = TRUE)
  q3 <- quantile(x, 0.75, na.rm = TRUE)
  iqr <- q3 - q1
  lower_bound <- q1 - 3 * iqr
  upper_bound <- q3 + 3 * iqr
  sum(x < lower_bound | x > upper_bound)
}

# Apply the function to each column in numeric_data
extreme_outlier_counts <- sapply(numeric_data, find_extreme_outlier_count)

# Create a data frame for display
outlier_table <- data.frame(Variable = names(extreme_outlier_counts), 
                            Outlier_Count = extreme_outlier_counts)

# Display the table
print(outlier_table)


#distribution
numeric_data_long <- pivot_longer(numeric_data, cols = everything(), names_to = "variable", values_to = "values")

numeric_data_long %>%
  ggplot(aes(x = values, fill = variable, color = variable)) +
  geom_histogram(bins = 15) +
  facet_wrap(~ variable, ncol = 2, scales = "free_y") +
  labs(x = "Values", y = "Frequency") +
  ggtitle("Histograms of Numeric Variables") +
  theme_minimal() +
  theme(legend.position = "none") +
  coord_cartesian(xlim = c(0,NA))


numeric_data_long %>%
  ggplot(aes(sample = values, color = variable)) +
  stat_qq() +
  stat_qq_line(col = "black") +
  facet_wrap(~ variable, ncol = 2, scales = "free") +
  labs(x = "Theoretical Quantiles", y = "Sample Quantiles") +
  ggtitle("Normal Probability Plots") +
  theme_minimal() +
  theme(legend.position = "none")

numeric_data_long <- pivot_longer(numeric_data, cols = everything(), names_to = "variable", values_to = "percentages")


numeric_data_long %>% ggplot(aes(y=percentages,x=variable,color=variable)) +
  stat_boxplot(geom ='errorbar') + 
  geom_boxplot() +
  labs(x = "Variables", y = "Percentages") +
  ggtitle("Box Plots") + theme_minimal() + theme(legend.position = "none") 




#normal bocplot
ggplot(data = my_data, aes(x = '', y = balance)) +
  geom_boxplot() +
  xlab('') +
  ylab('Balance') +
  ggtitle('Boxplot of Balance')



#improved boxplot
p <- ggplot(numeric_data, aes(x = factor(1), y = balance)) +
  geom_boxplot() +
  ggtitle("Boxplot of balance") +
  labs(x = "", y = "balance") 

#find three points 
top_outliers <- numeric_data$balance %>% 
  sort(decreasing = TRUE) %>% 
  head(3)

# Add red points for the top three outliers
p <- p + geom_point(data = numeric_data %>% filter(balance %in% top_outliers),
                    aes(x = factor(1), y = balance), 
                    color = "red")

#lablece
p <- p + geom_text(data = numeric_data %>% filter(balance %in% top_outliers),
                   aes(x = factor(1), y = balance, label = balance), 
                   vjust = -1.5, size = 3, hjust = 0.5)

# Display the plot
p



#druntation boxplot
ggplot(data = my_data, aes(x = '', y = duration)) +
  geom_boxplot() +
  xlab('') +
  ylab('Balance') +
  ggtitle('Boxplot of Balance')

#improved graph

p <- ggplot(numeric_data, aes(x = factor(1), y = duration)) +
  geom_boxplot() +
  ggtitle("Boxplot of duration") +
  labs(x = "", y = "Duration")  # Hide the dummy x-axis label

# Identify the six highest values in the duration column
top_outliers <- numeric_data$duration %>%
  sort(decreasing = TRUE) %>%
  head(7)

# Add points for the top six outliers
p <- p + geom_point(data = numeric_data %>% filter(duration %in% top_outliers),
                    aes(x = factor(1), y = duration),
                    color = "red")

# Optionally, add labels to the top six outliers
p <- p + geom_text(data = numeric_data %>% filter(duration %in% top_outliers),
                   aes(x = factor(1), y = duration, label = duration),
                   vjust = -1.5, size = 3, hjust = 0.5)

# Display the plot
p



#getting rid of the outliers

# Identify the top 3 outliers for 'balance'
balance_outliers <- my_data$balance %>% 
  sort(decreasing = TRUE) %>% 
  head(3)

# Identify the top 6 outliers for 'duration'
duration_outliers <- my_data$duration %>%
  sort(decreasing = TRUE) %>%
  head(6)

# Remove the rows for the top outliers in 'balance'
my_data_filtered <- my_data %>% 
  filter(!(balance %in% balance_outliers))

# Remove the rows for the top outliers in 'duration'
my_data_filtered <- my_data_filtered %>% 
  filter(!(duration %in% duration_outliers))




#relationships

# Normalized overlapped bar plots  exploration

#job
my_data %>% ggplot() + 
  geom_bar(aes(job,fill=y),position="fill") +
  scale_x_discrete( "job" ) + 
  scale_y_continuous( "Percent" ) + 
  guides(fill = guide_legend( title = "y" ) ) + 
  scale_fill_manual( values = c( "tomato", "skyblue3" ) )

#marital
my_data %>% ggplot() + 
  geom_bar(aes(marital,fill=y),position="fill") +
  scale_x_discrete( "marital status" ) + 
  scale_y_continuous( "Percent" ) + 
  guides(fill = guide_legend( title = "y" ) ) + 
  scale_fill_manual( values = c( "tomato", "skyblue3" ) )

#education
my_data %>% ggplot() + 
  geom_bar(aes(education,fill=y),position="fill") +
  scale_x_discrete( "education" ) + 
  scale_y_continuous( "Percent" ) + 
  guides(fill = guide_legend( title = "y" ) ) + 
  scale_fill_manual( values = c( "tomato", "skyblue3" ) )

#default
my_data %>% ggplot() + 
  geom_bar(aes(default,fill=y),position="fill") +
  scale_x_discrete( "default" ) + 
  scale_y_continuous( "Percent" ) + 
  guides(fill = guide_legend( title = "y" ) ) + 
  scale_fill_manual( values = c( "tomato", "skyblue3" ) )

#housing
my_data %>% ggplot() + 
  geom_bar(aes(housing,fill=y),position="fill") +
  scale_x_discrete( "housing" ) + 
  scale_y_continuous( "Percent" ) + 
  guides(fill = guide_legend( title = "y" ) ) + 
  scale_fill_manual( values = c( "tomato", "skyblue3" ) )
#loan
my_data %>% ggplot() + 
  geom_bar(aes(loan,fill=y),position="fill") +
  scale_x_discrete( "loan" ) + 
  scale_y_continuous( "Percent" ) + 
  guides(fill = guide_legend( title = "y" ) ) + 
  scale_fill_manual( values = c( "tomato", "skyblue3" ) )

#contact
my_data %>% ggplot() + 
  geom_bar(aes(contact,fill=y),position="fill") +
  scale_x_discrete( "contact" ) + 
  scale_y_continuous( "Percent" ) + 
  guides(fill = guide_legend( title = "y" ) ) + 
  scale_fill_manual( values = c( "tomato", "skyblue3" ) )

#month
fr

#poutcome
my_data %>% ggplot() + 
  geom_bar(aes(poutcome,fill=y),position="fill") +
  scale_x_discrete( "poutcome" ) + 
  scale_y_continuous( "Percent" ) + 
  guides(fill = guide_legend( title = "y" ) ) + 
  scale_fill_manual( values = c( "tomato", "skyblue3" ) )

#previous
my_data %>% ggplot() + 
  geom_bar(aes(previous,fill=y),position="fill") +
  scale_x_discrete( "previous" ) + 
  scale_y_continuous( "previous" ) + 
  guides(fill = guide_legend( title = "y" ) ) + 
  scale_fill_manual( values = c( "tomato", "skyblue3" ) )



#campaign
my_data %>% ggplot() + 
  geom_bar(aes(campaign,fill=y),position="fill") +
  scale_x_discrete( "job" ) + 
  scale_y_continuous( "campaign" ) + 
  guides(fill = guide_legend( title = "y" ) ) + 
  scale_fill_manual( values = c( "tomato", "skyblue3" ) )

#age
my_data %>% ggplot() + 
  geom_bar(aes(age,fill=y),position="fill") +
  scale_x_discrete( "job" ) + 
  scale_y_continuous( "Percent" ) + 
  guides(fill = guide_legend( title = "y" ) ) + 
  scale_fill_manual( values = c( "tomato", "skyblue3" ) )

barplot.norm <- function(data, x) {
  variable_name <- deparse(substitute(x))
  graph_title <- paste("Pass/Fail Distribution by", variable_name)
  ggplot(data, aes_string(x = variable_name, fill = "y")) +
    geom_bar(position = "fill") +
    labs(title = graph_title,
         x = variable_name,
         y = "Percentage") +
    theme_minimal() +
    scale_fill_brewer(palette = "Set1")
}
barplot.norm(my_data, previous)
my_data$previous_binned <- ifelse(my_data$previous > 0, "over_median", "at_or_below_median")

# Bin the 'age' variable into three categories
my_data$age_binned <- ifelse(my_data$age < 25, "young",
                             ifelse(my_data$age <= 65, "middle aged", "old"))

# Now, you can view the distribution of the binned age variable
table(my_data$age_binned, my_data$y)
barplot.norm(my_data, age_binned)




#frequency tables

#interpretation of the resulsts

#training and testing data
splitIndex <- createDataPartition(my_data_filtered$y, p = 0.7, list = FALSE)

# Creating training and testing datasets
trainData <- my_data_filtered[splitIndex, ]
testData <- my_data_filtered[-splitIndex, ]

#validate the split


#model 1


model <- rpart(y ~ ., data = trainData, method = "class")
printcp(model)
rpart.plot(model)

testData$y <- factor(testData$y, levels = levels(predictions))

predictions <- predict(model, testData, type = "class")
confusionMatrix(predictions, testData$y)



#model 2


sum(is.na(trainData))
colSums(is.na(trainData))

trainData <- trainData[, !(names(trainData) %in% c("campaign", "campaign_binned"))]

tuned_model <- train(y ~ ., data = trainData, method = "C5.0",
                     trControl = trainControl(method = "cv", number = 10),
                     tuneGrid = ctrl)
plot(tuned_model)

final_c50_model <- tuned_model$finalModel


print(final_c50_model$rules)


# Predict on the test set
testData$y <- factor(testData$y, levels = levels(test_predictions))


test_predictions <- predict(tuned_model, newdata = testData)

# Confusion Matrix
confusion <- confusionMatrix(test_predictions, testData$y)


# Print the confusion matrix
print(confusion)

# Print overall accuracy
cat("Accuracy:", confusion$overall['Accuracy'], "\n")




#model 2 try two
#code the best pssible c50 model for trainData$yTo code the best possible C5.0 model for your `trainData$y`, we can use the `C5.0()` function from the `C50` package. Here's a sample code to get you started:

library(C50)

trainData$y <- as.factor(trainData$y)

# Train the C5.0 model
model2 <- C5.0(y ~ ., data = trainData)

summary(model2)
plot(model2)

# Predict on the test set
testData$y <- factor(testData$y, levels = levels(test_predictions))


test_predictions <- predict(model2, newdata = testData)
test_predictions

# Confusion Matrix
confusion <- confusionMatrix(test_predictions, testData$y)
confusion



#model 3
#create a logistic regress# Assuming you have already loaded the necessary packages and have your data in the "trainData" dataframe

# Fit a logistic regression model using the "glm" function
model3 <- step(glm(y ~ ., data = trainData, family = binomial()))

summary(model3)



test_predictions <- predict(model3, newdata = testData, type = "response")

test_predictions_binary <- ifelse(test_predictions > 0.5, "yes", "no")

test_predictions_binary <- factor(test_predictions_binary, levels = levels(testData$y))
confusion_matrix <- confusionMatrix(test_predictions_binary, testData$y)

# Print the confusion matrix
print(confusion_matrix)
testData$y
levels(test_predictions_binary)




# The model can now be used to predict the values of "trainData$y" using new dataion model trying to predict the varible trainData$y. 
