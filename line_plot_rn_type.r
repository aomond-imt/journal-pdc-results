library("ggplot2")
library("dplyr")

# color=function(){scale_color_manual(values = c("#00AFBB", "#E7B800", "#FC4E07"))}

e = "total"
dodge = 5.5
for (t in c("clique", "star", "grid", "ring", "chain")) {
    d <- read.csv(glue::glue("e_{e}.csv"))
    d<-d %>% filter(net_tplgy == t)
#     d<-d %>% filter(srv_tplgy == "worst")
    unit <- if(e == "dynamic") "J" else "kJ"
    if (e == "dynamic") {
        color=function(){scale_color_manual(values = c("#00AFBB", "#E7B800", "#FC4E07"))}
    }
    else {
        color=function(){scale_color_manual(values = c("#b1c470", "#8370c4", "#FC4E07"))}
    }
#     d<-d %>% filter(srv_tplgy == "worst")
    ggplot(d, aes(x=size, y=energy_mean, shape=reorder(rn_type, srv_tplgy_index), colour=srv_tplgy)) +
        geom_errorbar(aes(ymin=energy_mean - energy_std, ymax=energy_mean + energy_std), width=.1, position=position_dodge(dodge), show.legend=FALSE) +
        geom_point(position=position_dodge(dodge)) +
        xlab("Number of ONs") +
        ylab(glue::glue("Accumulated energy consumption ({unit})")) +
        scale_x_continuous(breaks=unique(d$size)) +
        labs(colour="Physical topology:", shape="Type of RN:") +
#         theme(legend.position="top") +
        theme(legend.spacing = unit(-5, "pt"), legend.position="none", legend.box = "vertical",
              legend.key.size=unit(5, "points"), legend.text=element_text(size=5), legend.title=element_text(size=6), axis.text=element_text(size=7),
              axis.title.y=element_text(size=7, vjust=2.5), axis.title.x=element_text(size=7),
              panel.grid.minor.x=element_blank()) +
        guides(colour = guide_legend(override.aes = list(shape = 15))) +

#         scale_color_manual(values=c("#CC6666", "#9999CC"))
#         scale_y_continuous(n.breaks=12) +
        color()

    ggsave(glue::glue("line_plot_rn_type/{e}/{t}.pdf"), width=2, height=3)
}
