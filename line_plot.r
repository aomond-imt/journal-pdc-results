library("ggplot2")
library("dplyr")


e = "total"
for (t in c("No RN", "RN on agg", "RN not on agg")) {
    d <- read.csv(glue::glue("e_{e}.csv"))
    d<-d %>% filter(rn_type == t)
    ggplot(d, aes(x=size, y=energy_mean, colour=net_tplgy)) +
        geom_errorbar(aes(ymin=energy_mean - energy_std, ymax=energy_mean + energy_std), width=.1, position=position_dodge(0.5)) +
        geom_line() +
        facet_wrap(~ srv_tplgy) +
        geom_point(position=position_dodge(0.5)) +
        xlab("Number of ONs") +
        ylab("Accumulated energy consumption (J)") +
        scale_x_continuous(breaks=unique(d$size)) +
        labs(colour="Physical topology:") +
        theme(legend.position="top")

    ggsave(glue::glue("line_plot/{e}/{t}.pdf"), width=6, height=4)
}
