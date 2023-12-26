library("ggplot2")
d <- read.csv("e_dynamic.csv")

axis
ggplot(d, aes(x=size, y=energy_mean, colour=net_tplgy)) +
    geom_errorbar(aes(ymin=energy_mean - energy_std, ymax=energy_mean + energy_std), width=.1) +
    geom_line() +
    geom_point() + facet_wrap(~ srv_tplgy + rn_type) + xlab("Number of Observation Nodes") + ylab("Accumulated energy mean (J)") + scale_x_continuous(breaks=unique(d$size))

ggsave("e_dynamic.pdf", width=30, height=30)
