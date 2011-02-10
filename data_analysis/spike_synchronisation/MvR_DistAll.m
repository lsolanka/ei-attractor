function [D] = MvR_DistAll(neuronIDs, spikeCell, tc, dt, startTime, endTime, spikeNumThreshold)
% Compute MvR distance of all spike train pairs in the cell array set
% with time constant t_c
% For more informations cf. MCW van Rossum, A Novel spike distance, Neural
% computation, 2001

% Exponential
expo_dur = 10*tc; %sec
e_t = 0:dt:expo_dur;
expo = exp(-(e_t)/tc);
%expo = 1 - e_t/tc;
%expo = ones(1, numel(e_t));


N = numel(neuronIDs);
D = nan * ones(N);

for it = 1:N
    nid = neuronIDs(it);
    extractCell{it} = spikeCell{nid}(find(spikeCell{nid} >= startTime & spikeCell{nid} <= endTime));
end

for it1 = 1:N
    it1
    n1_spikeCnt = numel(extractCell{it1});
    if (n1_spikeCnt < spikeNumThreshold)
        continue;
    end
    response1 = createSpikeHistCell(it1, extractCell, dt, startTime, endTime);
    response1 = conv(response1, expo);
    
    for it2 = it1:N
        n2_spikeCnt = numel(extractCell{it2});
        if (n2_spikeCnt < spikeNumThreshold)
            continue;
        end

        response2 = createSpikeHistCell(it2, extractCell, dt, startTime, endTime);
        response2 = conv(response2, expo);
        % normalize against spike count
        spikeCnt_coeff = (n1_spikeCnt + n2_spikeCnt)/2;
        %spikeCnt_coeff = 1;
        D(it1, it2) = 1/tc * trapz((response1 - response2).^2)*dt / spikeCnt_coeff;
    end
end