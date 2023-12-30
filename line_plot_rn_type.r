library("ggplot2")
library("dplyr")


e = "dynamic"
for (t in c("clique", "star", "grid", "ring", "chain")) {
    d <- read.csv(glue::glue("e_{e}.csv"))
    d<-d %>% filter(net_tplgy == t)
    d<-d %>% filter(srv_tplgy == "worst")
    ggplot(d, aes(x=size, y=energy_mean, colour=rn_type)) +
        geom_errorbar(aes(ymin=energy_mean - energy_std, ymax=energy_mean + energy_std), width=.1, position=position_dodge(0.5)) +
        geom_line() +
        geom_point(position=position_dodge(0.5)) +
        xlab("Number of ONs") +
        ylab("Accumulated energy consumption (J)") +
        scale_x_continuous(breaks=unique(d$size)) +
        labs(colour="Physical topology:") +
        theme(legend.position="top")

    ggsave(glue::glue("line_plot_rn_type/{e}/{t}.pdf"), width=6, height=4)
}
