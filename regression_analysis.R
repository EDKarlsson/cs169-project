runtime_data <- read.csv('/Users/benjaminschrift/Documents/school/Current/cs-169/project/cs169-project/linedata.csv')

runtime_data[runtime_data$runtime > 35,] #get outliers
runtime_data <- runtime_data[-c(36,68,70,77,81),]

model = lm(runtime ~ variable_count, data=runtime_data)

plot(runtime_data$variable_count,resid(model))
qqnorm(resid(model))

plot(runtime_data$variable_count,runtime_data$runtime)
abline(model, col="red")

