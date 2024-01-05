library("ggplot2")
library("dplyr")

# color=function(){scale_fill_manual(values = c("#00AFBB", "#E7B800", "#FC4E07"))}

# t <- "clique"
# for (t in c("clique", "star", "grid", "ring", "chain")){
for (t in c("No RN", "RN on agg", "RN not on agg")){
    for (e_type in c("dynamic", "total")) {
        for (s in c(9, 25)) {
            d <- read.csv(glue::glue("e_{e_type}.csv"))
            d<-d %>% filter(rn_type == t)
            d<-d %>% filter(size == s)
            unit <- if(e_type == "dynamic") "J" else "kJ"
            if (e_type == "dynamic") {
                color=function(){scale_fill_manual(values = c("#00AFBB", "#E7B800", "#FC4E07"))}
            }
            else {
                color=function(){scale_fill_manual(values = c("#b1c470", "#8370c4", "#FC4E07"))}
            }
            ggplot(d, aes(x=reorder(net_tplgy, srv_tplgy_index), y=energy_mean, fill=srv_tplgy, label=energy_mean)) +
                geom_bar(color="black", stat = "identity", position = "dodge") +
                geom_errorbar(position=position_dodge(0.9), aes(ymin=energy_mean - energy_std, ymax=energy_mean + energy_std), width=.2, size=1) +
                geom_text(aes(y=min(energy_mean)/2), fill="white", fontface="bold", position=position_dodge(width=0.9)) +
                ylab(glue::glue("Accumulated energy consumption ({unit})")) +
                theme(axis.text.y = element_text()) +
                xlab(element_blank()) +
                labs(fill="Aggregation ON position:") +
                theme(legend.position="top", legend.text=element_text(size=15), legend.title=element_text(size=15), axis.text=element_text(size=15), axis.title.y=element_text(size=15, vjust=2.5)) +
                color()
            ggsave(glue::glue("bar_plot/{e_type}/{s}/{t}.pdf"), width=9, height=6)
        }
    }
}

warnings()
