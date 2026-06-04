package com.freshgrowth.batch.tasklet;

import com.freshgrowth.batch.shared.CtxKeys;
import org.springframework.batch.core.StepContribution;
import org.springframework.batch.core.scope.context.ChunkContext;
import org.springframework.batch.core.step.tasklet.Tasklet;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

@Component
public class SeoulMarketPriceCollectTasklet implements Tasklet {

    @Value("${garak.api.url}")
    private String apiUrl;

    @Value("${garak.api.id}")
    private String id;

    @Value("${garak.api.passwd}")
    private String passwd;

    @Value("${garak.api.dataid:data52}")
    private String dataid;

    @Value("${garak.api.pagesize:10}")
    private int pagesize;

    @Value("${garak.api.pageidx:1}")
    private int pageidx;

    @Value("${garak.api.portal-templet:false}")
    private boolean portalTemplet;

    @Value("${garak.api.p-ymd}")
    private String pYmd;

    @Value("${garak.api.p-jymd}")
    private String pJymd;

    @Value("${garak.api.d-cd:2}")
    private String dCd;

    @Value("${garak.api.p-jjymd}")
    private String pJjymd;

    @Value("${garak.api.p-pos-gubun:1}")
    private String pPosGubun;

    @Value("${garak.api.pum-nm:}")
    private String pumNm;

    private final RestClient restClient = RestClient.create();

    @Override
    public RepeatStatus execute(StepContribution contribution, ChunkContext chunkContext) {
        String url = buildUrl();
        String json = restClient.get()
                .uri(url)
                .retrieve()
                .body(String.class);

        if (json == null || json.isBlank()) {
            throw new IllegalStateException("서울시농수산식품공사 API 응답이 비어 있습니다.");
        }

        var ctx = chunkContext.getStepContext()
                .getStepExecution()
                .getJobExecution()
                .getExecutionContext();
        ctx.put(CtxKeys.PRICE_JSON, json);

        System.out.println("[Collect] Seoul market price API collected. url=" + maskKey(url));
        return RepeatStatus.FINISHED;
    }

    private String buildUrl() {
        return apiUrl
                + "?id=" + enc(id)
                + "&passwd=" + enc(passwd)
                + "&dataid=" + enc(dataid)
                + "&pagesize=" + pagesize
                + "&pageidx=" + pageidx
                + "&portal.templet=" + portalTemplet
                + "&p_ymd=" + enc(pYmd)
                + "&p_jymd=" + enc(pJymd)
                + "&d_cd=" + enc(dCd)
                + "&p_jjymd=" + enc(pJjymd)
                + "&p_pos_gubun=" + enc(pPosGubun)
                + "&pum_nm=" + enc(pumNm);
    }

    private String maskKey(String url) {
        if (passwd == null || passwd.length() < 4) {
            return url;
        }
        return url.replace(passwd, "***");
    }

    private String enc(String value) {
        if (value == null) {
            return "";
        }
        return URLEncoder.encode(value, StandardCharsets.UTF_8);
    }
}
