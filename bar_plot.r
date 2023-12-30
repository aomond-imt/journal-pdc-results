library("ggplot2")
library("dplyr")

# color=function(){scale_fill_manual(values = c("#00AFBB", "#E7B800", "#FC4E07"))}

# t <- "clique"
# for (t in c("clique", "star", "grid", "ring", "chain")){
for (t in c("No RN", "RN on agg", "RN not on agg")){
    for (e_type in c("dynamic", "total")) {
#         t <- "RN on agg"
#         e_type <- "total"
        d <- read.csv(glue::glue("e_{e_type}.csv"))
#         print(d)
#         d<-d %>% filter(net_tplgy == t)
        d<-d %>% filter(rn_type == t)
        d<-d %>% filter(size == 9)
#         d$srv_rn_tplgy <- paste(d$srv_tplgy,d$rn_type)
#         k<-arrange(d, rn_type, srv_tplgy)
        unit <- if(e_type == "dynamic") "J" else "kJ"
        if (e_type == "dynamic") {
            color=function(){scale_fill_manual(values = c("#00AFBB", "#E7B800", "#FC4E07"))}
        }
        else {
            color=function(){scale_fill_manual(values = c("#b1c470", "#8370c4", "#FC4E07"))}
        }
        # color=function(){scale_fill_manual(values = c("#b1c470", "#8370c4", "#FC4E07"))}
#         ggplot(d, aes(x=reorder(net_tplgy, srv_tplgy_index), y=energy_mean, fill=srv_tplgy, label=energy_mean)) +
        ggplot(d, aes(x=reorder(net_tplgy, srv_tplgy_index), y=energy_mean, fill=srv_tplgy, label=energy_mean)) +
            geom_bar(color="black", stat = "identity", position = "dodge") +
            geom_errorbar(position=position_dodge(0.9), aes(ymin=energy_mean - energy_std, ymax=energy_mean + energy_std), width=.2, size=1) +
#             geom_text(aes(y=min(energy_mean)/2), fill="white", fontface="bold", position=position_dodge(width=0.9)) +
#             geom_text(aes(y=2), fontface="bold", position=position_dodge(width=0.9)) +
            geom_text(aes(label = energy_mean, y = min(energy_mean)/2),vjust=-0.4,position=position_dodge(0.9),fontface="bold") +
        #     geom_label(data=d,aes(label = d$rn_type, y=35),label.padding=unit(0.35,"lines"),label.r=unit(0.09,"lines"),fill="#f0f0f0",label.size=0.5,fontface="bold",colour="black",position=position_dodge(0.9))+
            ylab(glue::glue("Accumulated energy consumption ({unit})")) +
            theme(axis.text.y = element_text()) +
            xlab(element_blank()) +
            labs(fill="Aggregation ON position:") +
            theme(legend.position="top", legend.text=element_text(size=15), legend.title=element_text(size=15), axis.text=element_text(size=15), axis.title.y=element_text(size=15, vjust=2.5)) +
            color()
        ggsave(glue::glue("plots_paper_per_tplgy/{e_type}/{t}.pdf"), width=8, height=6)
    }
}

warnings()
